from functools import wraps
from django.shortcuts import redirect

def require_header(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'X-Template-Only' in request.headers:
            return view_func(request, *args, **kwargs)
        return redirect('/#/not-found')
    return wrapper

# def jwt_auth_required(view_func):
# 	@wraps(view_func)
# 	def wrapped_view(request, *args, **kwargs):
# 		logger.debug(f"Request headers: {request.headers}")
# 		try:
# 			# Attempt JWT authentication
# 			jwt_auth = JWTAuthentication()
# 			auth_result = jwt_auth.authenticate(request)
# 			if auth_result is None:
# 				# No token or invalid token
# 				return JsonResponse({'message': 'Not authenticated'}, status=403)
				
# 			# Authentication successful, set user and continue
# 			request.user = auth_result[0]
# 			return view_func(request, *args, **kwargs)
			
# 		except AuthenticationFailed as e:
# 			logger.error(f"Authentication failed: {str(e)}")
# 			return JsonResponse({'message': str(e)}, status=403)
			
# 	return wrapped_view