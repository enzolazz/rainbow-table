import enum
from rich.console import Console
from rich.theme import Theme


class Status(enum.Enum):
    """Defines the semantic type of a log message, decoupled from color."""

    SUCCESS = "success"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class Logger:
    """A centralized logger that uses rich for beautiful, consistent output."""

    def __init__(self):
        custom_theme = Theme(
            {
                "success": "green",
                "info": "cyan",
                "warning": "yellow",
                "error": "bold red",
            }
        )
        self.console = Console(theme=custom_theme)

    def _log(self, message: str, status: Status):
        """Internal log handler."""
        self.console.print(
            f"==> [{status.value}][{status.value.upper()}][/{status.value}] {message}",
            highlight=False,
        )

    def success(self, message: str):
        """Logs a success message."""
        self._log(message, Status.SUCCESS)

    def info(self, message: str):
        """Logs an info message."""
        self._log(message, Status.INFO)

    def warning(self, message: str):
        """Logs a warning message."""
        self._log(message, Status.WARNING)

    def error(self, message: str):
        """Logs an error message."""
        self._log(message, Status.ERROR)


log = Logger()
