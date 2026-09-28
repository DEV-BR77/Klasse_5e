"""Protected integration and export formats for django-model-visualizer."""

import csv
import io
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET

from model_visualizer.forms import ModelFilterForm
from model_visualizer.serializers import build_graph_payload
from model_visualizer.views import ModelGraphPageView

from .ui_views import _require_portal_admin


def _payload(request):
    filter_keys = set(request.GET.keys()) - {"format"}
    if not filter_keys:
        return build_graph_payload({
            "app_label": None,
            "include_auto_created": False,
            "include_proxy": False,
            "include_django_apps": False,
        }), None
    form = ModelFilterForm(request.GET or None)
    if not form.is_valid():
        return None, form
    return build_graph_payload(form.cleaned_data), form


def _guard(request):
    _require_portal_admin(request.user)


@login_required
@require_GET
def graph(request):
    _guard(request)
    return ModelGraphPageView.as_view()(request)


@login_required
@require_GET
def graph_api(request):
    _guard(request)
    payload, form = _payload(request)
    if payload is None:
        return JsonResponse({"message": "Ungültige Filterangaben.", "errors": form.errors}, status=400)
    return JsonResponse(payload)


def _rows(payload):
    model_rows = []
    field_rows = []
    edge_rows = []
    for model in payload["models"]:
        model_rows.append(
            [
                model["id"],
                model["app_label"],
                model["name"],
                model["verbose_name"],
                model["db_table"],
            ]
        )
        for field in model["fields"]:
            field_rows.append(
                [
                    model["id"],
                    field["name"],
                    field["kind"],
                    field["type"],
                    field.get("relation_target") or "",
                    field["null"],
                    field["blank"],
                    field["primary_key"],
                    field["unique"],
                    field["db_index"],
                ]
            )
    for edge in payload["edges"]:
        edge_rows.append([edge["from"], edge["to"], edge["field"], edge["type"]])
    return model_rows, field_rows, edge_rows


def _csv_response(payload, delimiter, extension, content_type):
    model_rows, field_rows, edge_rows = _rows(payload)
    output = io.StringIO(newline="")
    writer = csv.writer(output, delimiter=delimiter, lineterminator="\n")
    writer.writerow(["Django-Modellvisualisierung"])
    writer.writerow(["Modelle", payload["meta"]["model_count"], "Beziehungen", payload["meta"]["edge_count"]])
    writer.writerow([])
    writer.writerow(["Modelle"])
    writer.writerow(["ID", "App", "Name", "Anzeigename", "Datenbanktabelle"])
    writer.writerows(model_rows)
    writer.writerow([])
    writer.writerow(["Felder"])
    writer.writerow(["Modell", "Feld", "Art", "Typ", "Beziehung zu", "NULL", "Leer", "Primärschlüssel", "Eindeutig", "Index"])
    writer.writerows(field_rows)
    writer.writerow([])
    writer.writerow(["Beziehungen"])
    writer.writerow(["Von", "Nach", "Feld", "Typ"])
    writer.writerows(edge_rows)
    response = HttpResponse(output.getvalue(), content_type=content_type)
    response["Content-Disposition"] = f'attachment; filename="klassid-modellgraph.{extension}"'
    return response


@login_required
@require_GET
def export_graph(request):
    _guard(request)
    payload, form = _payload(request)
    if payload is None:
        return JsonResponse({"message": "Ungültige Filterangaben.", "errors": form.errors}, status=400)

    export_format = request.GET.get("format", "json").lower()
    if export_format == "json":
        response = JsonResponse(payload, json_dumps_params={"ensure_ascii": False, "indent": 2})
        response["Content-Disposition"] = 'attachment; filename="klassid-modellgraph.json"'
        return response
    if export_format == "csv":
        return _csv_response(payload, ",", "csv", "text/csv; charset=utf-8")
    if export_format == "tsv":
        return _csv_response(payload, "\t", "tsv", "text/tab-separated-values; charset=utf-8")
    if export_format == "markdown":
        model_rows, field_rows, edge_rows = _rows(payload)
        lines = ["# KlassID Django-Modellgraph", "", f"Modelle: {len(model_rows)}", f"Beziehungen: {len(edge_rows)}", "", "## Modelle", "", "| Modell | App | Tabelle |", "|---|---|---|"]
        lines.extend(f"| {row[2]} | {row[1]} | {row[4]} |" for row in model_rows)
        lines.extend(["", "## Felder", "", "| Modell | Feld | Typ | Beziehung zu |", "|---|---|---|---|"])
        lines.extend(f"| {row[0]} | {row[1]} | {row[3]} | {row[4]} |" for row in field_rows)
        response = HttpResponse("\n".join(lines), content_type="text/markdown; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="klassid-modellgraph.md"'
        return response
    if export_format == "xlsx":
        return _xlsx_response(payload)
    return JsonResponse({"message": "Format nicht unterstützt. Erlaubt: json, csv, tsv, markdown, xlsx."}, status=400)


def _xlsx_response(payload):
    from openpyxl import Workbook

    model_rows, field_rows, edge_rows = _rows(payload)
    workbook = Workbook()
    sheets = [
        ("Übersicht", [["KlassID Django-Modellgraph"], ["Modelle", len(model_rows)], ["Beziehungen", len(edge_rows)]]),
        ("Modelle", [["ID", "App", "Name", "Anzeigename", "Datenbanktabelle"], *model_rows]),
        ("Felder", [["Modell", "Feld", "Art", "Typ", "Beziehung zu", "NULL", "Leer", "Primärschlüssel", "Eindeutig", "Index"], *field_rows]),
        ("Beziehungen", [["Von", "Nach", "Feld", "Typ"], *edge_rows]),
    ]
    for index, (title, rows) in enumerate(sheets):
        sheet = workbook.active if index == 0 else workbook.create_sheet()
        sheet.title = title
        for row in rows:
            sheet.append(row)
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions
        for column in sheet.columns:
            width = min(max(max(len(str(cell.value or "")) for cell in column) + 2, 12), 48)
            sheet.column_dimensions[column[0].column_letter].width = width
        for cell in sheet[1]:
            cell.font = cell.font.copy(bold=True)
    stream = io.BytesIO()
    workbook.save(stream)
    response = HttpResponse(stream.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="klassid-modellgraph.xlsx"'
    return response
