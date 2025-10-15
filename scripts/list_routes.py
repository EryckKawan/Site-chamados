from app import app
for rule in sorted(app.url_map.iter_rules(), key=lambda r: (r.endpoint, r.rule)):
    methods = ','.join(sorted(rule.methods - set(['HEAD','OPTIONS'])))
    print(f"{rule.endpoint:40} {methods:12} {rule.rule}")
