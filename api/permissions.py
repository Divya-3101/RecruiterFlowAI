from rest_framework.permissions import BasePermission


class IsRecruiter(BasePermission):
    message = "Only recruiters are allowed."

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and request.user.role == 'recruiter'
        )


class IsCandidate(BasePermission):
    message = "Only candidates are allowed."
    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and request.user.role == 'candidate'
        )

class IsJobOwnerOrReadOnly(BasePermission):
    message = "You can only modify your own job."
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):

        if request.method == 'GET':
            return True

        return (
            request.user.role == 'recruiter'
            and obj.recruiter == request.user
        )