from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("hotels")


@mcp.tool()
def fetch_travelplan():
    """hotels에서 숙소 정보를 가져오는 함수

    Returns:
        json
    """
    url = "http://127.0.0.1:8000/hotels"
    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


if __name__ == "__main__":
    print("Starting MCP server...")
    mcp.run()
