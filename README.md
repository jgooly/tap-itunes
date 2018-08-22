# iTunes Tap
Author: Julian Ganguli

[Singer](singer.io) tap that produces JSON-formatted data following
the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md) (mostly).

Get daily data from iTunes Reporter for the subscription and subscription event reports.

Official iTunes Connect report documentation can be found here:
https://help.apple.com/itc/appssalesandtrends/

Report specific documentation can be found here:
https://help.apple.com/itc/appssalesandtrends/#/itc37a18bcbf

### Installation

To run locally, clone this repo, then run:

```bash
pip install -e .
```

Now you can run:
```bash
tap-itunes --config config.json
```

Optionally, you can pass state.json to sync from the last completed sync date.
```bash
tap-itunes --config config.json --state state.json
```

### How it works

For a given date, this tap will fetch the daily subscription and subscription event
reports.

### Configuration example
See the `example_config.json` file in the taps main directory to get started.
Each field will need to be populated. See the iTunes Report Guide for more information.

### State file
If you would like to run incremental jobs, you can use a state file.
This file will keep track of the last success tap run and start the next 
run from the previously store state.

This file should be placed in the tap's main directory.

The state file should contain `subscription` and `subscription_event` objects with date values
in a YYYY-MM-DD format.
 
 You can quickly create a state file by running the following command.
```bash
echo '{"subscription": "YYYY-MM-DD", "subscription_event": "YYYY-MM_DD"}' > state.json
```
See `example_state.json` as reference.

### Output format
* Column headers are transformed to downcased and spaces are replaced with "_".
* The Subscription stream has an added "date" column that includes the date for
the individual record. Without the "date" column, there would be now way to
know which records belong to which dates. This particular iTunes report encodes the
data's date in the file name and this value is used to populate the "date" field.