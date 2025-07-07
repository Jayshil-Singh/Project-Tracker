import streamlit_authenticator as stauth
 
hashed_passwords = stauth.Hasher(['admin']).generate()
print(hashed_passwords) 