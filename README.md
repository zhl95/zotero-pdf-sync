# zotero-pdf-sync
a python script synchronizes pdf documents between zotero dataset and customized path for further sync like dropbox and mobile devices.


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

pyzotero


### Installing

pip install pyzotero 

## Running the tests

1. Edit and library_id and api key following tutorial of pyzotero.
2. Edit the Zotero/storage directory of your Zotero Installation: win_basepath
3. Edit the target path you want to sync with (such as a Dropbox folder): pad_basepath

4. python zotero-sync.py


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Zotero
* pyzotero
