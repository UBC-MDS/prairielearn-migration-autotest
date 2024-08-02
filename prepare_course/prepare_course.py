from create_instance import create_instance



try:
    result = create_instance("../pl-ubc-dsci571", "F20", "Fall 2020")
except Exception as e:
    print(f"Error: {e}")
else:
    print(result)