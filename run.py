from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    # 使用socketio.run替代app.run
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)