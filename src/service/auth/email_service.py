async def send_otp_email(
    email: str,
    otp: str,
):
    print("=" * 50)
    print(f"Sending OTP to: {email}")
    print(f"OTP: {otp}")
    print("=" * 50)