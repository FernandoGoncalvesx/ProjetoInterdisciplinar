from backend.models.noticia import listar_noticias as buscar_noticias


if __name__ == "__main__":
    from backend.services.coleta_noticias import crawler_noticias
    print(crawler_noticias()["mensagem"])
