
with open(r'c:\Users\usEr\Desktop\projectnew\app\templates\teacher_dashboard.html', 'w', encoding='utf-8') as f:
    f.write("""<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <title>Teacher Admin</title>
</head>
<body>
    <h1>Dashboard</h1>
    <p>User: {{ user }}</p>
    <div>
        High: {{ stats['distribution']['High (8-10)'] }}<br>
        Mid: {{ stats['distribution']['Mid (5-7)'] }}<br>
        Low: {{ stats['distribution']['Low (0-4)'] }}
    </div>
</body>
</html>""")
