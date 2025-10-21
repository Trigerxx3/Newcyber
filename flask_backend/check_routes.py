from app import create_app

app = create_app()

print("=== All registered routes ===")
for rule in app.url_map.iter_rules():
    print(f"{rule.methods} {rule.rule} -> {rule.endpoint}")

print("\n=== Case activities routes ===")
for rule in app.url_map.iter_rules():
    if 'activities' in rule.rule:
        print(f"{rule.methods} {rule.rule} -> {rule.endpoint}")
