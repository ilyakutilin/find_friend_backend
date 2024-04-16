def set_request_server(result, generator, request, public):
    """Установка адреса сервера для Swagger."""
    if request:
        url = request.build_absolute_uri("/api/v1/")
        result.setdefault("servers", []).append({"url": url})
    return result
