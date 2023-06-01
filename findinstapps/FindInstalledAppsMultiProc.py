import argparse
import json
import os
import multiprocessing

class FindInstalledApps:
    def __init__(self, config_file):
        self.config = self.load_config(config_file)
        self.exclusions = self.config.get("exclusions", [])
        self.num_processes = self.config.get("num_processes", 1)
        self.search_paths = self.config.get("search_paths", [])
        self.extension = self.config.get("extension", "")

    def load_config(self, config_file):
        with open(config_file) as f:
            config = json.load(f)
        return config

    def search(self):
        processes = []
        results = multiprocessing.Manager().list()

        for path in self.search_paths:
            process = multiprocessing.Process(target=self.search_path, args=(path, results))
            process.start()
            processes.append(process)

        for process in processes:
            process.join()

        # Flatten the results list
        flattened_results = [item for sublist in results for item in sublist]

        # Filter out excluded paths
        filtered_results = [result for result in flattened_results if not self.is_excluded(result)]

        # Print the final list of found files
        for result in filtered_results:
            print(result)


    def search_path(self, path, results):
        found_files = []
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(self.extension):
                    full_path = os.path.join(root, file)
                    found_files.append(full_path)
                    print(full_path)
        results.append(found_files)

    def is_excluded(self, path):
        for exclusion in self.exclusions:
            if exclusion in path:
                return True
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find Installed Applications")
    parser.add_argument("-c", "--config", help="Path to the JSON configuration file", required=True)
    args = parser.parse_args()

    finder = FindInstalledApps(args.config)
    finder.search()

