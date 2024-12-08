# from fasthtml.common import *
# from dataclasses import dataclass
# app, rt = fast_app()
# @dataclass
# class User:
#     username: str
#     email: str
#     password: str
# def validate_user(user: User):
#     errors = []
#     if len(user.username) < 3:
#         errors.append("Username must be at least 3 characters long")
#         if '@' not in user.email:
#             errors.append("Invalid email address")
#             if len(user.password) < 8:
#                 errors.append("Password must be at least 8 characters long")
#                 return errors
# @rt("/")
# def get():
#     return Titled("User Registration",
#                   Form(Input(type="text", name="username", placeholder="Username"),
#                        Input(type="email", name="email", placeholder="Email"),
#                        Input(type="password", name="password", placeholder="Password"),
#                        Button("Register", type="submit"),
#                        hx_post="/register",
#                        hx_target="#result"
#                        ),
#                        Div(id="result")
#                        )
# @rt("/register")
# def post(user: User):
#     errors = validate_user(user)
#     if errors:
#         return Div(Ul(*[Li(error) for error in errors]), id="result", style="color: red;")
#     return Div(f"Registered: {user.username} ({user.email})", id="result", style="color: green;")
# serve()

# from fasthtml.common import *
# from fasthtml.oauth import GitHubAppClient, redir_url
# import os
# # # Set up a database
# db = database('data/user_counts.db') # type: ignore
# user_counts = db.t.user_counts
# if user_counts not in db.t:
#     user_counts.create(dict(name=str, count=int), pk='name')
# Count = user_counts.dataclass()

# # Auth client setup for GitHub
# client = GitHubAppClient(os.getenv("AUTH_CLIENT_ID"), 
#                          os.getenv("AUTH_CLIENT_SECRET"))
# redir_path = "/auth_redirect"


# # Beforeware that puts the user_id in the request scope or redirects to the login page if not logged in.
# def before(req, session):
#     # The `auth` key in the scope is automatically provided to any handler which requests it, and can not
#     # be injected by the user using query params, cookies, etc, so it should be secure to use.
#     auth = req.scope['auth'] = session.get('user_id', None)
#     # If the session key is not there, it redirects to the login page.
#     if not auth: return RedirectResponse('/login', status_code=303)
#     # If the user is not in the database, redirect to the login page.
#     if auth not in user_counts: return RedirectResponse('/login', status_code=303)
#     # Ensure user can only see their own counts:
#     user_counts.xtra(name=auth)
# bware = Beforeware(before, skip=['/login', '/auth_redirect'])

# app = FastHTML(before=bware)

# # Homepage (only visible if logged in)
# @app.get('/')
# def home(auth):
#     return Div(
#         P("Count demo"),
#         P(f"Count: ", Span(user_counts[auth].count, id='count')),
#         Button('Increment', hx_get='/increment', hx_target='#count'),
#         P(A('Logout', href='/logout'))  # Link to log out,
#     )

# @app.get('/increment')
# def increment(auth):
#     c = user_counts[auth]
#     c.count += 1
#     return user_counts.upsert(c).count

# # The login page has a link to the GitHub login page.
# @app.get('/login')
# def login(request):
#     redir = redir_url(request, redir_path)
#     return Div(P("You are not logged in."), 
#                A('Log in with GitHub', href=client.login_link(redir)))

# # To log out, we just remove the user_id from the session.
# @app.get('/logout')
# def logout(session):
#     session.pop('user_id', None)
#     return RedirectResponse('/login', status_code=303)

# # The redirect page is where the user is sent after logging in.
# @app.get('/auth_redirect')
# def auth_redirect(code: str, request, session, state: str = None):
#     redir = redir_url(request, redir_path)
#     if not code: return "No code provided!"
#     print(f"code: {code}")
#     print(f"state: {state}") # Not used in this example.
#     try:
#         # The code can be used once, to get the user info:
#         info = client.retr_info(code, redir)
#         print(f"info: {info}")
#         # Use client.retr_id(code) directly if you just want the id, otherwise get the id with:
#         user_id = info[client.id_key]
#         print(f"User id: {user_id}")
#         # Access token (populated after retr_info or retr_id) - unique to this user,
#         # and sometimes used to revoke the login. Not used in this case.
#         token = client.token["access_token"]
#         print(f"access_token: {token}")

#         # We put the user_id in the session, so we can use it later.
#         session['user_id'] = user_id

#         # We also add the user in the database, if they are not already there.
#         if user_id not in user_counts:
#             user_counts.insert(name=user_id, count=0)

#         # Redirect to the homepage
#         return RedirectResponse('/', status_code=303)

#     except Exception as e:
#         print(f"Error: {e}")
#         return f"Could not log in."

# serve()