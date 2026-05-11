import os
import json
from mcp.server.fastapi import Context
from mcp.server import Server
from mcp.types import Tool, TextContent
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange, Dimension, Metric, RunReportRequest
)
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# Configuración básica
server = Server("talentopolis-analytics")

def get_analytics_client():
    token_path = os.path.join(os.path.dirname(__file__), 'token.json')
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/analytics.readonly'])
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return BetaAnalyticsDataClient(credentials=creds)
    raise Exception("No se encontro token.json. Autenticate primero.")

def get_prop_id():
    # Intentar leer desde .env
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith("GA4_PROPERTY_ID="):
                    return line.split("=")[1].strip()
    return os.getenv("GA4_PROPERTY_ID")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_active_users_by_city",
            description="Obtiene el numero de usuarios activos por ciudad en los ultimos 7 dias.",
            input_schema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_device_report",
            description="Obtiene un listado historico de los dispositivos (mobile/desktop) conectados.",
            input_schema={
                "type": "object",
                "properties": {},
            },
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    client = get_analytics_client()
    prop_id = get_prop_id()
    
    if not prop_id:
        return [TextContent(type="text", text="Error: No se encontro el Property ID de Analytics.")]

    if name == "get_active_users_by_city":
        request = RunReportRequest(
            property=f"properties/{prop_id}",
            dimensions=[Dimension(name="city")],
            metrics=[Metric(name="activeUsers")],
            date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
        )
        response = client.run_report(request)
        result = "Usuarios Activos por Ciudad (7 dias):\n"
        for row in response.rows:
            result += f"- {row.dimension_values[0].value}: {row.metric_values[0].value} usuarios\n"
        return [TextContent(type="text", text=result)]

    elif name == "get_device_report":
        request = RunReportRequest(
            property=f"properties/{prop_id}",
            dimensions=[Dimension(name="deviceCategory"), Dimension(name="mobileDeviceModel")],
            metrics=[Metric(name="activeUsers")],
            date_ranges=[DateRange(start_date="2020-01-01", end_date="today")],
        )
        response = client.run_report(request)
        result = "Reporte Historico de Dispositivos:\n"
        for row in response.rows:
            result += f"- {row.dimension_values[0].value} ({row.dimension_values[1].value}): {row.metric_values[0].value} usuarios\n"
        return [TextContent(type="text", text=result)]

    return [TextContent(type="text", text=f"Herramienta desconocida: {name}")]

if __name__ == "__main__":
    from mcp.server.stdio import stdio_server
    import asyncio

    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())

    asyncio.run(run())
