# IFCViz
A tool to visualize IFC files in a browser

![image](https://github.com/IFCViz/IFCViz/assets/48377932/104b250a-5cf9-4f9e-b8c9-1aa0c59b8cd9)


## Dependencies
- Flask:
```bash
pip3 install flask
pip3 install ifcopenshell
pip3 install lark
```
- Docker
- Docker compose
```bash
sudo npm install --global yarn
```
- Doxygen (optional, for generating documentation)
  
## Submodules
Fetch them using:
```bash
git submodule update --init
```

## How to run the server?
#### Start the database:  
```sh
docker compose up
```  
  
#### Start the Flask backend server:
```bash
cd api/ && flask run
```

## Documentation generation
Run ```doxygen``` in the project root to generate a documentation website in ``/html`` and latex documentation in ``/latex``. Code commented with triple single-quotes will ne included in the generated documentation. 

  
### Other Documentation
[IFC.js](https://docs.thatopen.com/Tutorials/FragmentIfcLoader)
