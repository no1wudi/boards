class Kconfig:
    """
    A parser for Kconfig configuration files.

    This class provides functionality to read and verify Kconfig configurations
    from a .config file. It supports checking for the presence of specific
    configurations and validating required configuration options.

    Private Attributes:
        _config_path (str): Path to the .config file
        _config_lines (list): Content of the config file

    Example:
        kconfig = Kconfig("/path/to/.config")
        if kconfig.has_config("CONFIG_EXAMPLE"):
            print("Configuration found")
    """
    def __init__(self, config_path):
        """Initialize Kconfig parser with path to .config file."""
        self._config_path = config_path
        self._config_lines = []
        self._read_config()

    def _read_config(self):
        """Read and store configuration from .config file."""
        try:
            with open(self._config_path, "r") as f:
                self._config_lines = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {self._config_path}")

    def has_config(self, config):
        """Check if a specific configuration exists."""
        return config in self._config_lines

    def check_configs(self, required_configs):
        """Check if all required configurations are present."""
        return all(self.has_config(config) for config in required_configs)

    def get_value(self, config_name):
        """
        Get the value of a configuration option.

        Args:
            config_name (str): Name of the configuration option (e.g. CONFIG_UART0_BAUD)

        Returns:
            str or None: The value of the config if found, None otherwise
            For boolean configs (CONFIG_XXX=y), returns 'y'
            For numeric/string configs (CONFIG_XXX=123), returns the value after '='
        """
        if not isinstance(self._config_lines, str):
            return None

        for line in self._config_lines.splitlines():
            line = line.strip()
            if line.startswith(config_name + '='):
                value = line.split('=', 1)[1]
                return value
        return None
