else:

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        try:
            user = auth.sign_in_with_email_and_password(
                email.strip(),
                password
            )

            st.session_state.user = user
            st.session_state.user_email = email

            st.rerun()

        except Exception as e:
            st.error(f"Login failed: {str(e)}")
