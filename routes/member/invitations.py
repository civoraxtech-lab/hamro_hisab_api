from flask import g, request
from flask_restx import Namespace, Resource, fields
from utils.decorators import token_required
from services.invitation_service import InvitationService

invitations_ns = Namespace('invitations', description='Group invitation operations', path='/api/invitations')

accept_model = invitations_ns.model('AcceptInvitation', {
    'profile_id': fields.String(required=True, example='uuid-here'),
})


@invitations_ns.route('/')
class InvitationList(Resource):
    @invitations_ns.doc(security='Bearer')
    @token_required
    def get(self):
        """List pending invitations for the current user"""
        return InvitationService.get_pending_for_user(g.user.id), 200


@invitations_ns.route('/<string:invitation_id>/accept')
class InvitationAccept(Resource):
    @invitations_ns.doc(security='Bearer')
    @invitations_ns.expect(accept_model)
    @token_required
    def post(self, invitation_id):
        """Accept an invitation using the chosen profile"""
        profile_id = (request.json or {}).get('profile_id')
        if not profile_id:
            return {'message': 'profile_id is required'}, 400
        result, status = InvitationService.accept(invitation_id, g.user.id, profile_id)
        return result, status


@invitations_ns.route('/<string:invitation_id>/reject')
class InvitationReject(Resource):
    @invitations_ns.doc(security='Bearer')
    @token_required
    def post(self, invitation_id):
        """Reject an invitation"""
        result, status = InvitationService.reject(invitation_id, g.user.id)
        return result, status
