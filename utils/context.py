from flask import request, abort
from db.models import Profile

def get_active_profile(user_id):
    profile_id = request.headers.get('X-Profile-ID')
    if profile_id:
        # SECURITY: Verify ownership — prevents cross-user profile access
        profile = Profile.query.filter_by(id=profile_id, user_id=user_id, deleted_at=None).first()
        if not profile:
            abort(403, description="You do not have permission to access this profile")
        return profile

    # No header provided — fall back to default profile, then first available
    profile = Profile.query.filter_by(user_id=user_id, is_default=True, deleted_at=None).first()
    if not profile:
        profile = Profile.query.filter_by(user_id=user_id, deleted_at=None).first()
    if not profile:
        abort(400, description="No active profile found. Please create a profile first.")
    return profile