from flask import render_template

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        return render_template('base.html', error_title='Bad Request', error_msg='The request was invalid or could not be understood.'), 400

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('base.html', error_title='Access Forbidden', error_msg='You do not have permission to view or modify this resource.'), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template('base.html', error_title='Page Not Found', error_msg='The requested resource was not found on this server.'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template('base.html', error_title='Internal Server Error', error_msg='An unexpected error occurred. Please try again later.'), 500
