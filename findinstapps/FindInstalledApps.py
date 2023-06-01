import os
import json
import threading

class FindInstalledApps:
    def __init__(self, exclusions=[]):
        self.exclusions = exclusions
        self.results = []

    def search_executables(self, root_path):
        for root, dirs, files in os.walk(root_path):
            for file in files:
                if self.is_mac_executable(file):
                    full_path = os.path.join(root, file)
                    self.results.append(full_path)
                    print(full_path)

    def is_mac_executable(self, file_name):
        _, ext = os.path.splitext(file_name)
        return ext.lower() == ".app"

    def load_exclusions_from_json(self, json_file):
        with open(json_file) as f:
            data = json.load(f)
            self.exclusions = data["exclusions"]

    def run_search(self, paths, num_threads=10):
        threads = []
        for path in paths:
            thread = threading.Thread(target=self.search_executables, args=(path,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    def get_results(self):
        return self.results


# Example usage
if __name__ == "__main__":
    # Create FindInstalledApps instance
    finder = FindInstalledApps()

    # Load exclusions from JSON file
    finder.load_exclusions_from_json("exclusions_mac.json")

    # Define search paths
    search_paths = ["/Applications"]

    # Run the search with 10 threads
    finder.run_search(search_paths, num_threads=10)

    # Get the results
    results = finder.get_results()

    # Print the results
    #for result in results:
    #    print(result)
    # print the amount of the file-results
    print("Amount of files: " + str(len(results)))