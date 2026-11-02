import os
import flet as ft
from app.ui import create_app


def start():
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "7080"))

    app_target = create_app()

    # Support both Flet 1.x (ft.run) and Flet 0.x (ft.app)
    if hasattr(ft, "run"):
        ft.run(
            main=app_target,
            host=host,
            port=port,
            view=ft.AppView.WEB_BROWSER,
        )
    elif hasattr(ft, "app"):
        getattr(ft, "app")(
            target=app_target,
            host=host,
            port=port,
            view=getattr(ft.AppView, "WEB_BROWSER", None),
        )


def main():
    start()


if __name__ == "__main__":
    main()
