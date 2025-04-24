from flasklibrary import app,db,scheduler
from flasklibrary.routes import generate_and_cleanup_code
import os
from flasklibrary.models import User,AdminCode
from flasklibrary.routes import create_default_admin


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # User.__table__.drop(db.engine)
        # AdminCode.__table__.drop(db.engine)
        create_default_admin()
    

# Only add the job if it doesn't already exist
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        if not scheduler.get_job('admin_code_job'):
            scheduler.add_job(
                    id='admin_code_job',
                    func=generate_and_cleanup_code,
                    trigger='interval',
                    seconds=62
                )
 
    app.run(debug=True)

# with app.app_context()

