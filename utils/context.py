from flask import request, abort
from db.models import Profile

def get_active_profile(user_id):
    profile_id = request.headers.get('X-Profile-ID')
    if not profile_id:
        abort(400, description="Active profile context (X-Profile-ID) missing")
    # SECURITY: Verify ownership
    # This prevents User A from accessing User B's profile ID
    profile = Profile.query.filter_by(id=profile_id, user_id=user_id).first()
    if not profile:
        abort(403, description="You do not have permission to access this profile")
        
    return profile