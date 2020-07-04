# gitchm
A CLI tool that lets you replicate a git repo's commit history without reproducing the working tree. It works by creating commits in the destination repo using the details (author, committer, timestamp, and message) of commits from the source repo. Changes to the destination working tree are made only by writing the commit messages into an auto-generated text file. Files and directories from the source repo are not copied.

The current version of the tool allows you to:
- Choose a local git repo as the source repo
- Specify a local directory or git repo as the destination (or let the tool generate the destination for you)
- Query commits by author, committer, and timestamp
- Select which branch to copy commits from as well as which branch to copy commits into

## Current Version
0.1.0

## Requirements
- [Python](https://www.python.org/downloads/release/python-380/) >= 3.8+
- [Git](https://git-scm.com/) 1.7.0 or newer
- [gitpython](https://github.com/gitpython-developers/GitPython) >=3.1.3

Please see `requirements.txt` and `dev-requirements.txt` for full list of dependencies.

## Installation
1. Create and activate a virtual environment
2. Run the following:
    ```console
    $ pip install git+https://github.com/ralphqq/gitchm
    ```

## Usage
Make sure that the virtual environment where you pip installed gitchm is activated. Then run:

```console
$ gitchm
```

The tool then asks you to enter the following details:
- **Path to source repository:** The absolute path to the directory containing the source repository. This is a required item, and the path must point to a valid git repo.
- **Path to destination repository:** The absolute path to the destination repository. This is an optional item. If not provided, a new directory will be generated for you. The value can be a path to a non-existent directory (in that case, it will be created); a path to an empty or valid git repo; or a path to a directory that has previously been used as a destination repo.
- **Prefix to identify auto-generated destination directory:** Prefix to be pre-appended to the auto-generated destination repo. This item is optional. If not provided, the string 'mirror-' will be pre-appended to the name of the source directory in order to create the destination folder.
- **Author name or email to query commits:** All or part of the commit author's name or email address. This item is optional and is not case sensitive.
- **Committer name or email to query commits:** All or part of the committer's name or email address. This item is optional and is not case sensitive.
- **Query commits before date/time:** Date/Time string of the form yyyy-mm-dd HH:MM:SS (time component can be excluded). This item is optional.
- **Query commits after date/time:** Date/Time string of the form yyyy-mm-dd HH:MM:SS (time component can be excluded). This item is optional.
- **Branch in source repo to get commits from:** Name of branch in source repo. This is optional. If not provided, the currently active branch is used.
- **Branch in destination repo to copy commits into:** Name of branch in destination repo. This is optional. If not provided, the currently active branch is used.

## Development Setup
1. Clone this repo
2. Create and activate a virtual environment
3. Install the development dependencies:
    ```console
    $ pip install -r dev-requirements.txt
    ```
4. Run the test suite:
    ```console
    $ pytest
    ```

## Contributing
1. Fork this repo
2. Clone your fork into your local machine
3. Follow steps in Development Setup but skip step 1
4. Create your feature branch:
    ```console
    $ git checkout -b feature/some-new-thing
    ```
5. Commit your changes:
    ```console
    $ git commit -m "Develop new thing"
    ```
6. Push to the branch:
    ```console
    $ git push origin feature/some-new-thing
    ```
7. Create a pull request

## License
gitchm is available under the [MIT License](https://opensource.org/licenses/MIT).
