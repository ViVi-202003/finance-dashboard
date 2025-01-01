# Finance dashboard

Tool to analyze income and expenses, similar to apps like Finanzguru.

![Screenshot](screenshot.png)

Has three parts:
- Grafana dashboard that shows the data
- Postgres database as data source for Grafana
- Syncer script that imports data from a bank account

Currently the following banks are supported:
- ING (DE)

## Quickstart

```bash
docker-compose up
```

Then visit [http://localhost:3000](http://localhost:3000). You will find a Grafana dashboard with some example data.

[!TIP]
The default login is `admin`/`admin`. You can change the password in the Grafana settings.

## Loading in your own data

Make sure to have a fresh database. It's easiest to remove the complete deployment and start over:

```bash
docker-compose down -v
```

Now you need two things: 
- A banking data importer plugin: see the example importer in `plugins/example_importer``
- A classifier plugin: see the example classifier in `plugins/example_classifier`

For a real-world example, see the ING DE CSV importer in `plugins/ing_de_csv_importer`. This plugin uses the CSV data that can be exported on the ING banking dashboard.

When you have your plugin(s), set the environment variables `IMPORTER_PLUGIN` and `CLASSIFIER_PLUGIN` to the Python path of the plugin. Then start the deployment:

```bash
export IMPORTER_PLUGIN="plugins.example_importer.importer"
export CLASSIFIER_PLUGIN="plugins.example_classifier.classifier"
docker-compose up
```

## License

`MIT`
