# Tyche front end

This is a nice visual representation of what happens in the backend of Tyche. It is a simple web interface that
allows users to enter values and see the results of the backend calculations. The project uses Flask and integrates
with Mapbox to display the results on a map.

## Installation
Setup is simple, first clone the repository and then install the dependencies.

```bash
make install
```
OR
```bash
pip install -r requirements.txt
```

Then to run the application, simply run the following command:

```bash
flask --app app/router.py run
```
