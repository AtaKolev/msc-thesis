import yaml

class YAMLParser:

    @staticmethod
    def read_yaml_file(file_path):
        """
        Read a YAML file and return its content as a dictionary.

        Args:
        - file_path (str): Path to the YAML file.

        Returns:
        - dict: Content of the YAML file as a dictionary.
        """
        with open(file_path, 'r') as file:
            try:
                yaml_data = yaml.safe_load(file)
                return yaml_data
            except yaml.YAMLError as exc:
                print(f"Error reading YAML file: {exc}")
                return None