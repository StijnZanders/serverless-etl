def test(arg):
    import pandas as pd
    from datetime import datetime

    df = pd.DataFrame([[datetime.now(), arg]], columns=["current_timestamp", "message"])
    df.to_gbq("test_dataset.test_table", if_exists="append")

def test_multiple_outputs(arg):
    return ["test1", "test2"]

def test_with_context(arg, context):
    import pandas as pd
    from datetime import datetime

    print(context)

    df = pd.DataFrame([[datetime.now(), arg]], columns=["current_timestamp", "message"])
    df.to_gbq("test_dataset.test_table", if_exists="append")
