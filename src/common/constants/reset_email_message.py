class EmailTemplates:
    RESET_PASSWORD = """
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                color: #333;
                background-color: #f9f9f9;
                margin: 0;
                padding: 0;
            }}
            .container {{
                width: 100%;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #ffffff;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
            h2 {{
                color: #2c3e50;
            }}
            p {{
                font-size: 16px;
                line-height: 1.5;
            }}
            .cta-btn {{
                display: inline-block;
                padding: 12px 25px;
                font-size: 16px;
                color: #fff;
                background-color: #3498db;
                text-decoration: none;
                border-radius: 4px;
                margin-top: 20px;
            }}
            .cta-btn:hover {{
                background-color: #2980b9;
            }}
            .footer {{
                margin-top: 30px;
                font-size: 12px;
                color: #aaa;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>비밀번호 초기화 요청</h2>
            <p>안녕하세요, {user_name}님.</p>
            <p>비밀번호를 초기화하려면 아래 링크를 클릭하세요:</p>
            <a href="{reset_link}" class="cta-btn">비밀번호 초기화</a>
            <p>링크는 24시간 동안 유효합니다.</p>
            <p class="footer">이 이메일은 자동으로 생성된 이메일입니다. 답변하지 마세요.</p>
        </div>
    </body>
    </html>
    """
