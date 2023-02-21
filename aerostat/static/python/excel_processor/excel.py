import re
import uuid
import xml.etree.ElementTree as ET
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED

XML_DECLARATION = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n'


def _register_all_namespaces(xml_content: bytes):
    namespaces = dict(
        [node for _, node in ET.iterparse(BytesIO(xml_content), events=["start-ns"])]
    )
    for ns in namespaces:
        ET.register_namespace(ns, namespaces[ns])
    return namespaces


def _update_table_file(
    table_file_content: bytes, column_names: list[str]
) -> tuple[bytes, list[str]]:
    """Update the table file in the openXML file.

    There are three references need to be updated besides the columns themselves:
    1. root element: tableColumns.attrib["ref"]
    2. autoFilter element: attrib["ref"]
    3. tableColumns elements: attrib["count"]
    """
    _register_all_namespaces(table_file_content)
    table_root = ET.fromstring(table_file_content)

    # update references
    ref = f"A1:{chr(65 + len(column_names) - 1)}2"
    table_root.attrib["ref"] = ref
    table_root.find(".//{*}autoFilter").attrib["ref"] = ref
    columns = table_root.find(".//{*}tableColumns")
    columns.attrib["count"] = str(len(column_names))

    # record original column names and replace with new column names in table file
    original_column_names = [
        original_column.attrib["name"]
        for original_column in columns.findall(".//{*}tableColumn")
    ]
    for original_column in columns.findall(".//{*}tableColumn"):
        columns.remove(original_column)
    for index, column in enumerate(column_names):
        ET.SubElement(
            columns,
            "tableColumn",
            attrib={
                "id": str(index + 1),
                "{http://schemas.microsoft.com/office/spreadsheetml/2016/revision3}uid": "{"
                + str(uuid.uuid4()).upper()
                + "}",
                "name": column,
            },
        )

    return (
        XML_DECLARATION + ET.tostring(table_root),
        original_column_names,
    )


def _update_shared_string_file(
    shared_string_file_content: bytes,
    original_column_names: list[str],
    new_column_names: list[str],
    api_endpoint: str,
) -> tuple[bytes, list[str], dict[str, str]]:
    """Update the sharedString file in the openXML file.
    Returns updated file content, new column ids, and other ids that need to be updated.
    """
    _register_all_namespaces(shared_string_file_content)
    shared_strings_root = ET.fromstring(shared_string_file_content)

    shared_strings = shared_strings_root.findall(".//{*}si")

    # update api endpoint
    shared_strings[3].find(".//{*}t").text = api_endpoint

    # insert new columns
    original_ids = {}
    for index, string in enumerate(shared_strings):
        string_text = string.find(".//{*}t").text
        original_ids[string_text] = str(index)
        if string_text in original_column_names:
            shared_strings_root.remove(string)
    for new_column in new_column_names:
        si = ET.SubElement(shared_strings_root, "si")
        t = ET.SubElement(si, "t")
        t.text = new_column

    # record new column ids
    new_strings = shared_strings_root.findall(".//{*}si")
    column_ids = [
        str(i)
        for i in range(len(new_strings) - len(new_column_names), len(new_strings))
    ]

    # produce id mapping for shifted shared strings
    new_ids = {}
    for index, string in enumerate(new_strings):
        new_ids[string.find(".//{*}t").text] = str(index)
    id_mapping = {
        old_id: new_id
        for old_string, old_id in original_ids.items()
        for new_string, new_id in new_ids.items()
        if old_string == new_string
    }

    shared_strings_root.attrib["count"] = str(
        len(shared_strings_root.findall(".//{*}si"))
    )

    return XML_DECLARATION + ET.tostring(shared_strings_root), column_ids, id_mapping


def _update_sheet_file(
    sheet_file_content: bytes,
    column_ids: list[str],
    id_mapping: dict[str, str],
) -> bytes:
    """Update the sheet file in the openXML file."""
    namespaces = _register_all_namespaces(sheet_file_content)
    sheet_root = ET.fromstring(sheet_file_content)

    # update total column count
    sheet_data = sheet_root.find(".//{*}sheetData")
    rows = sheet_data.findall(".//{*}row")
    rows_to_update = rows

    # if link to table, update new columns
    if sheet_root.find(".//{*}tableParts") is not None:
        header_row, *rows_to_update = rows
        header_row.attrib["spans"] = f"1:{len(column_ids)}"
        for cell in header_row.findall(".//{*}c"):
            header_row.remove(cell)
        for index, column_id in enumerate(column_ids):
            c = ET.SubElement(
                header_row,
                "c",
                attrib={
                    "r": f"{chr(65 + index)}1",
                    "t": "s",
                },
            )
            v = ET.SubElement(c, "v")
            v.text = column_id

    # update all rows
    for row in rows_to_update:
        for cell in row.findall(".//{*}c"):
            if cell.attrib.get("t") == "s":
                original_id = cell.find(".//{*}v").text
                cell.find(".//{*}v").text = id_mapping[original_id]

    # force to add all namespaces. this is because python xml module removes unused namespaces,
    # see https://stackoverflow.com/questions/45990761/why-does-xml-package-modify-my-xml-file-in-python3
    for prefix, uri in namespaces.items():
        if prefix and prefix not in ET._namespaces(sheet_root)[1].values():
            ET.register_namespace(prefix, uri)  # Ensure correct prefixes in output
            sheet_root.set(
                "xmlns:" + prefix, uri
            )  # Add ns declarations to root element

    return XML_DECLARATION + ET.tostring(sheet_root)


def update_excel(
    openXML_file_path: str,
    column_names: list[str],
    api_endpoint,
    output_file_path="/tmp/template.xlsm",
    table_name="INPUT_TABLE",
) -> dict[str, bytes]:
    """Main function for modifying table columns in the openXML file."""

    with ZipFile(openXML_file_path, "r") as template_file:
        files = {file: template_file.read(file) for file in template_file.namelist()}

    # find xml file for the table
    table_filename = [
        file
        for file, file_content in files.items()
        if file.endswith(".xml") and table_name.encode("utf-8") in file_content
    ][0]
    # update table file
    files[table_filename], original_column_names = _update_table_file(
        files[table_filename], column_names
    )

    # update column names in shared strings file
    shared_strings_file = [
        file for file, file_content in files.items() if "sharedStrings.xml" in file
    ][0]
    files[shared_strings_file], column_ids, id_mapping = _update_shared_string_file(
        files[shared_strings_file],
        original_column_names=original_column_names,
        new_column_names=column_names,
        api_endpoint=api_endpoint,
    )

    # update column names in shared strings file
    sheet_files = [
        file
        for file, file_content in files.items()
        if re.search(r"sheet\d{1,2}.xml$", file)
    ]
    for sheet_file in sheet_files:
        files[sheet_file] = _update_sheet_file(
            files[sheet_file], column_ids, id_mapping
        )

    with ZipFile(output_file_path, "w", compression=ZIP_DEFLATED) as output_file:
        for file, file_content in files.items():
            output_file.writestr(file, file_content)

    return files


if __name__ == "__main__":
    update_excel(
        openXML_file_path="/Users/vincentyan/PycharmProjects/Aerostat/aerostat/static/template.xlsm",
        column_names=["a", "b", "c"],
        api_endpoint="http://localhost:5000",
        output_file_path="/Users/vincentyan/Downloads/dryrun.xlsm",
    )
