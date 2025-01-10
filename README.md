# ft_transcendence
Final project of the 42 Common Core

django tldr:

🔹 **Models** (Data Containers):
```python
# Like C++ classes that map to database tables
class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
```

🔹 **Forms** (Input Handling/Validation):
```python
# Like std::cin + validation
class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(min_length=8)
```

🔹 **Views** (Request Handlers):
```python
# Like API endpoints that process requests
def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Save to database
            return redirect('success')
    return render(request, 'login.html', {'form': form})
```

Flow:
1. URL routes to View
2. View processes request
3. Form validates input
4. Model handles data storage
5. View returns response

Think:
- Models = Database tables
- Forms = Input validation
- Views = Request processors


## PostgreSQL TLDR

### Basic Commands
```bash
# Login to PostgreSQL
psql -U postgres                    # As postgres user
psql -U django_user -d django_db    # As specific user/database
PGPASSWORD=mypass psql -U user -d db # With password

# Inside PSQL
\du          # List users and roles
\l           # List databases
\dt          # List tables in current db
\d tablename # Describe table structure
\c dbname    # Connect to database
\q           # Quit
\x           # Toggle expanded display
\timing      # Toggle query timing

# SQL Queries 
SELECT * FROM tablename;          # Show all rows
SELECT * FROM tablename LIMIT 5;  # Show first 5 rows
SELECT column1, column2 FROM tablename; # Show specific columns