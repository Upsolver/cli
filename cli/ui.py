import dataclasses
import time
from datetime import datetime
from threading import Thread
from typing import Any, Callable

from prompt_toolkit.application import Application, get_app
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.key_binding.key_bindings import KeyBindings, merge_key_bindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.widgets import Button, Dialog, Frame, Label, RadioList, TextArea
from tabulate import tabulate


def prompt_choose_dialog(title: str, values: list) -> Any:
    radio_list = RadioList(values)

    def ok_handler() -> None:
        get_app().exit(result=radio_list.current_value)

    dialog = Dialog(
        title=title,
        body=HSplit(
            [Label(text=title, dont_extend_height=False), radio_list],
            padding=1,
        ),
        buttons=[
            Button(text='Ok', handler=ok_handler),
        ],
        with_background=True
    )

    app = Application(
        layout=Layout(dialog),
        key_bindings=merge_key_bindings([load_key_bindings()]),
        mouse_support=True,
        full_screen=False
    )

    return app.run()


def stats_screen(title: str,
                 headers: list,
                 get_values: Callable[[], list],
                 interval_sec: float = 0.5) -> None:
    txt_area = TextArea(read_only=True)
    layout = Layout(container=Frame(
        txt_area,
        title=title,
    ))

    kb = KeyBindings()

    @kb.add('q')
    def _(event: Any) -> None:
        event.app.exit()

    application = Application(
        layout=layout,
        key_bindings=kb,
        full_screen=True,
    )

    stop_updating = False

    def update_stats() -> None:
        while not stop_updating:
            txt_area.text = \
                f'last refreshed at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n' + \
                tabulate(
                    [dataclasses.asdict(v).values() for v in get_values()],
                    headers=headers
                )
            time.sleep(interval_sec)

    thread = Thread(target=update_stats)
    thread.start()
    application.run()
    stop_updating = True
    thread.join(timeout=0.5)
