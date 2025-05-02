from itertools import chain
from  django . shortcuts  import  get_object_or_404, render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from . models import  ConnectionRequest, LikePost, Post, Profile
from django.db.models import Q




def signup(request):
 try:
    if request.method == 'POST':
        fnm=request.POST.get('fnm')
        emailid=request.POST.get('emailid')
        pwd=request.POST.get('pwd')
        phone=request.POST.get('phone')
        
        # Basic phone number validation
        if not phone.isdigit() or len(phone) < 10:
            invalid = "Please enter a valid phone number (at least 10 digits)"
            return render(request, 'signup.html', {'invalid': invalid})
            
        print(fnm,emailid,pwd,phone)
        my_user=User.objects.create_user(fnm,emailid,pwd)
        my_user.save()
        user_model = User.objects.get(username=fnm)
        new_profile = Profile.objects.create(user=user_model, id_user=user_model.id, phone=phone)
        new_profile.save()
        
        # Instead of logging in and redirecting to home, redirect to login page
        return redirect('/loginn')
    
        
 except:
        invalid="User already exists"
        return render(request, 'signup.html',{'invalid':invalid})
  
    
 return render(request, 'signup.html')
        
     
        
        
        
        
    

def loginn(request):
 
  if request.method == 'POST':
        fnm=request.POST.get('fnm')
        pwd=request.POST.get('pwd')
        print(fnm,pwd)
        
        # Try to authenticate with username
        userr = authenticate(request, username=fnm, password=pwd)
        
        # If authentication failed, try to find user by phone number
        if userr is None:
            try:
                # Find profile with matching phone number
                profile = Profile.objects.get(phone=fnm)
                # Get the user associated with this profile
                userr = authenticate(request, username=profile.user.username, password=pwd)
            except Profile.DoesNotExist:
                userr = None
        
        if userr is not None:
            login(request,userr)
            return redirect('/')
        
 
        invalid="Invalid Credentials"
        return render(request, 'loginn.html',{'invalid':invalid})
               
  return render(request, 'loginn.html')

@login_required(login_url='/loginn')
def logoutt(request):
    logout(request)
    return redirect('/loginn')



@login_required(login_url='/loginn')
def home(request):
    current_user = request.user
    posts = Post.objects.all().order_by('-created_at')  # Show all posts
    profile = Profile.objects.get(user=current_user)
    liked_post_ids = LikePost.objects.filter(username=current_user.username).values_list('post_id', flat=True)
    liked_posts = [str(uuid_str) for uuid_str in liked_post_ids]
    connections = User.objects.none()  # Or fetch as needed

    context = {
        'posts': posts,
        'profile': profile,
        'liked_posts': liked_posts,
        'connections': connections,
    }
    return render(request, 'main.html', context)


    


@login_required(login_url='/loginn')
def upload(request):
    current_user = request.user

    # Fetch connections
    connections_sender = ConnectionRequest.objects.filter(sender=current_user, is_accepted=True).values_list('receiver', flat=True)
    connections_receiver = ConnectionRequest.objects.filter(receiver=current_user, is_accepted=True).values_list('sender', flat=True)
    connection_user_ids = connections_sender.union(connections_receiver)
    connections = User.objects.filter(id__in=connection_user_ids)

    if request.method == 'POST':
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']
        
        # Handle allowed viewers
        allowed_viewer_ids = request.POST.getlist('allowed_viewers') # Get list of selected user IDs
        
        # Validate that selected users are actual connections
        allowed_viewers_qs = connections.filter(id__in=allowed_viewer_ids)

        new_post = Post.objects.create(
            user=current_user.username,  # Store username as before
            image=image, 
            caption=caption
        )
        
        # Set the allowed viewers using the validated queryset
        new_post.allowed_viewers.set(allowed_viewers_qs)
        
        # Note: We are not saving the post here because set() does it. 
        # If you were adding one by one with .add(), you'd need new_post.save() after the loop.

        return redirect('/')
    else:
        # Pass connections to the context for the GET request (when showing the form)
        # This assumes the upload form is displayed elsewhere, not via this view directly
        # If the upload form IS rendered by this view on GET, you'd need a render() call here.
        # For now, it redirects on GET, so this context passing might not be used yet.
        # We might need to adjust where the upload form is rendered.
        context = {'connections': connections}
        # return render(request, 'your_upload_form_template.html', context) # Example if rendering a form
        return redirect('/') # Current behavior

@login_required(login_url='/loginn')
def likes(request, id):
    post = get_object_or_404(Post, id=id)
    username = request.user.username

    like = LikePost.objects.filter(post_id=str(post.id), username=username).first()

    if like:
        # Unlike
        like.delete()
        post.no_of_likes -= 1
    else:
        # Like
        LikePost.objects.create(post_id=str(post.id), username=username)
        post.no_of_likes += 1

    post.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))

# @login_required(login_url='/loginn')
# def explore(request):
#     # Only show posts that are public (allowed_viewers is null)
#     posts = Post.objects.filter(allowed_viewers__isnull=True).order_by('-created_at') # Changed from Post.objects.all()
#     profile = Profile.objects.get(user=request.user)

#     # Get liked posts for the current user (Ensure comparison works with UUIDs if post.id is UUID)
#     liked_post_ids = LikePost.objects.filter(username=request.user.username).values_list('post_id', flat=True)
#     liked_posts = [str(uuid_str) for uuid_str in liked_post_ids]

#     context={
#         'post': posts, # Changed variable name from 'post' to 'posts' for consistency
#         'profile':profile,
#         'liked_posts': liked_posts,
#     }
#     return render(request, 'explore.html',context)
    
@login_required(login_url='/loginn')
def profile(request, id_user):
    user_object = User.objects.get(username=id_user)
    profile = Profile.objects.get(user=request.user)
    user_profile = Profile.objects.get(user=user_object)
    
    # New query: Filter posts for the profile being viewed (user_object)
    # Show posts if: 
    # 1. The visitor is the profile owner (request.user == user_object) -> show all their posts
    # 2. The visitor is NOT the owner: show posts where allowed_viewers is null OR visitor is in allowed_viewers
    if request.user == user_object:
        # Profile owner sees all their own posts
        user_posts = Post.objects.filter(user=user_object.username).order_by('-created_at')
    else:
        # Visitor sees posts by user_object that are public (null allowed_viewers) OR explicitly allowed for visitor
        visible_posts_query = (
            Q(allowed_viewers__isnull=True) |
            Q(allowed_viewers=request.user)
        )
        user_posts = Post.objects.filter(user=user_object.username).filter(visible_posts_query).distinct().order_by('-created_at')
        
    user_post_length = user_posts.count() # Use count() for efficiency

    # Get the User objects for the follower and receiver
    follower = request.user
    receiver = User.objects.get(username=id_user)

    # Check if the current user is following the profile user
    if ConnectionRequest.objects.filter(sender=follower, receiver=receiver).first():
        follow_unfollow = 'Remove Connection'
    else:
        follow_unfollow = 'Add Connection'

    # Get user connections
    user_connections = User.objects.filter(
        Q(received_requests__sender=receiver, received_requests__is_accepted=True) |
        Q(sent_requests__receiver=receiver, sent_requests__is_accepted=True)
    ).exclude(id=receiver.id)

    # Get current user's connections
    current_user_connections = User.objects.filter(
        Q(received_requests__sender=follower, received_requests__is_accepted=True) |
        Q(sent_requests__receiver=follower, sent_requests__is_accepted=True)
    ).exclude(id=follower.id)

    # Get mutual connections
    mutual_connections = user_connections.filter(
        id__in=current_user_connections.values_list('id', flat=True)
    )

    # Get liked posts for the current user
    liked_posts = [str(post_id) for post_id in LikePost.objects.filter(username=request.user.username).values_list('post_id', flat=True)]

    # Counting accepted connections for the profile user
    user_followers = len(ConnectionRequest.objects.filter(
        Q(receiver=receiver, is_accepted=True) | 
        Q(sender=receiver, is_accepted=True)
    ))
    
    # Counting accepted connections for the logged-in user
    user_following = len(ConnectionRequest.objects.filter(
        Q(receiver=follower, is_accepted=True) | 
        Q(sender=follower, is_accepted=True)
    ))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'profile': profile,
        'follow_unfollow': follow_unfollow,
        'user_followers': user_followers,
        'user_following': user_following,
        'user_connections': user_connections,
        'mutual_connections': mutual_connections,
        'liked_posts': liked_posts,
    }
    
    # Fetch logged-in user's connections for the upload modal (if applicable on this page)
    logged_in_user = request.user
    connections_sender = ConnectionRequest.objects.filter(sender=logged_in_user, is_accepted=True).values_list('receiver', flat=True)
    connections_receiver = ConnectionRequest.objects.filter(receiver=logged_in_user, is_accepted=True).values_list('sender', flat=True)
    connection_user_ids = connections_sender.union(connections_receiver)
    connections = User.objects.filter(id__in=connection_user_ids)
    context['connections'] = connections # Add connections to context
    
    if request.user.username == id_user:
        if request.method == 'POST':
            if request.FILES.get('image') == None:
                image = user_profile.profileimg
                bio = request.POST['bio']
                location = request.POST['location']

                user_profile.profileimg = image
                user_profile.bio = bio
                user_profile.location = location
                user_profile.save()
            if request.FILES.get('image') != None:
                image = request.FILES.get('image')
                bio = request.POST['bio']
                location = request.POST['location']

                user_profile.profileimg = image
                user_profile.bio = bio
                user_profile.location = location
                user_profile.save()

            return redirect('/profile/'+id_user)
        else:
            return render(request, 'profile.html', context)
    
    return render(request, 'profile.html', context)



@login_required(login_url='/loginn')
def delete(request, id):
    try:
        # Get the post and ensure it belongs to the current user
        post = Post.objects.get(id=id, user=request.user.username)
        post.delete()
        # Redirect to the user's profile after deletion
        return redirect('/profile/'+ request.user.username)
    except Post.DoesNotExist:
        # Post not found or doesn't belong to the user
        # Redirect back to home or show an error message (redirecting for simplicity)
        return redirect('/') 
    except Exception as e:
        # Handle other potential errors (optional: log the error)
        print(f"Error deleting post {id}: {e}") # Basic logging
        return redirect('/') # Redirect on error


@login_required(login_url='/loginn')
def search_results(request):
    query = request.GET.get('q')
    current_user = request.user

    # Get all users that match the search query
    all_users = Profile.objects.filter(
        Q(user__username__icontains=query) |  # Search by username
        Q(user__email__icontains=query) |     # Search by email
        Q(phone__icontains=query)             # Search by phone number
    ).exclude(user=current_user)  # Exclude the current user
    
    # Get connected users (users with accepted connections)
    connected_user_ids = set()
    accepted_connections = ConnectionRequest.objects.filter(
        Q(sender=current_user, is_accepted=True) | 
        Q(receiver=current_user, is_accepted=True)
    )
    
    for connection in accepted_connections:
        if connection.sender == current_user:
            connected_user_ids.add(connection.receiver.id)
        else:
            connected_user_ids.add(connection.sender.id)
    
    # Get users with similar attributes
    similar_user_ids = set()
    
    # Get users with similar email domains
    if '@' in query:
        email_domain = query.split('@')[1]
        similar_email_users = User.objects.filter(
            email__icontains=email_domain
        ).exclude(id=current_user.id)
        for user in similar_email_users:
            similar_user_ids.add(user.id)
    
    # Get users with similar phone numbers (if phone numbers are in the same area code)
    if query.isdigit() and len(query) >= 3:
        area_code = query[:3]  # Assuming first 3 digits are area code
        similar_phone_users = User.objects.filter(
            profile__phone__startswith=area_code
        ).exclude(id=current_user.id)
        for user in similar_phone_users:
            similar_user_ids.add(user.id)
    
    # Get users with similar usernames
    if len(query) >= 3:
        username_prefix = query[:3]  # First 3 characters of query
        similar_username_users = User.objects.filter(
            username__startswith=username_prefix
        ).exclude(id=current_user.id)
        for user in similar_username_users:
            similar_user_ids.add(user.id)
    
    # Split users into connected, similar, and other
    connected_users = all_users.filter(user_id__in=connected_user_ids)
    similar_users = all_users.filter(user_id__in=similar_user_ids).exclude(user_id__in=connected_user_ids)
    other_users = all_users.exclude(user_id__in=connected_user_ids).exclude(user_id__in=similar_user_ids)
    
    # Combine the lists with connected users first, then similar users, then others
    users = list(connected_users) + list(similar_users) + list(other_users)
    
    # Get posts that match the search query
    posts = Post.objects.filter(caption__icontains=query)

    context = {
        'query': query,
        'users': users,
        'posts': posts,
        'connected_count': len(connected_users),
        'similar_count': len(similar_users),
        'other_count': len(other_users),
    }
    return render(request, 'search_user.html', context)

def home_post(request, id):
    post = Post.objects.get(id=id)
    profile = Profile.objects.get(user=request.user)
    context = {
        'post': post,
        'profile': profile
    }
    return render(request, 'main.html', context)



# def follow(request):
#     if request.method == 'POST':
#         follower = request.POST['follower']
#         user = request.POST['user']

#         if Followers.objects.filter(follower=follower, user=user).first():
#             delete_follower = Followers.objects.get(follower=follower, user=user)
#             delete_follower.delete()
#             return redirect('/profile/'+user)
#         else:
#             new_follower = Followers.objects.create(follower=follower, user=user)
#             new_follower.save()
#             return redirect('/profile/'+user)
#     else:
#         return redirect('/')



@login_required
def connect(request):
    if request.method == 'POST':
        sender = request.user
        receiver_username = request.POST['user']
        receiver = User.objects.get(username=receiver_username)

        # Check if there's an existing request from the sender to the receiver
        existing_request = ConnectionRequest.objects.filter(sender=sender, receiver=receiver).first()
        
        # Check if there's a reverse request from the receiver to the sender
        reverse_request = ConnectionRequest.objects.filter(sender=receiver, receiver=sender).first()

        # If there's an existing request, delete it (unfollow)
        if existing_request:
            existing_request.delete()
            return redirect('/profile/' + receiver.username)
        
        # If there's a reverse request, accept it (mutual connection)
        elif reverse_request:
            # Accept the reverse request
            reverse_request.is_accepted = True
            reverse_request.save()
            
            # Create a new accepted request from sender to receiver to ensure both users have a connection record
            new_request = ConnectionRequest.objects.create(sender=sender, receiver=receiver, is_accepted=True)
            new_request.save()
            
            return redirect('/profile/' + receiver.username)

        # If no existing requests, create a new one
        else:
            # Create a new connection request and immediately accept it
            new_request = ConnectionRequest.objects.create(sender=sender, receiver=receiver, is_accepted=True)
            new_request.save()
            
            # Check if there's already a pending request from the receiver to the sender
            # If so, automatically accept both requests to create a mutual connection
            pending_reverse = ConnectionRequest.objects.filter(sender=receiver, receiver=sender, is_accepted=False).first()
            if pending_reverse:
                # Accept the reverse request
                pending_reverse.is_accepted = True
                pending_reverse.save()
            
            return redirect('/profile/' + receiver.username)
        
    return redirect('/')

@login_required(login_url='/loginn')
def get_user_recommendations(request):
    current_user = request.user
    current_profile = Profile.objects.get(user=current_user)
    
    # Get users with similar email domains
    email_domain = current_user.email.split('@')[1] if '@' in current_user.email else ''
    similar_email_users = User.objects.filter(
        email__endswith=email_domain
    ).exclude(id=current_user.id)
    
    # Get users with similar phone numbers (if phone numbers are in the same area code)
    similar_phone_users = User.objects.none()
    if current_profile.phone:
        area_code = current_profile.phone[:3]  # Assuming first 3 digits are area code
        similar_phone_users = User.objects.filter(
            profile__phone__startswith=area_code
        ).exclude(id=current_user.id)
    
    # Get users with similar usernames
    username_prefix = current_user.username[:3]  # First 3 characters of username
    similar_username_users = User.objects.filter(
        username__startswith=username_prefix
    ).exclude(id=current_user.id)
    
    # Combine all recommendations and remove duplicates
    recommended_users = list(set(list(similar_email_users) + 
                              list(similar_phone_users) + 
                              list(similar_username_users)))
    
    # Get profiles for recommended users
    recommended_profiles = Profile.objects.filter(user__in=recommended_users)
    
    # Exclude users that the current user already has an accepted connection with
    existing_connections = ConnectionRequest.objects.filter(
        Q(sender=current_user, is_accepted=True) | Q(receiver=current_user, is_accepted=True)
    ).values_list('sender', 'receiver')
    
    connected_user_ids = set()
    for sender, receiver in existing_connections:
        connected_user_ids.add(sender.id)
        connected_user_ids.add(receiver.id)
    
    recommended_profiles = recommended_profiles.exclude(user_id__in=connected_user_ids)
    
    context = {
        'recommended_profiles': recommended_profiles,
        'profile': current_profile
    }
    
    return render(request, 'recommendations.html', context)

@login_required(login_url='/loginn')
def search_suggestions(request):
    query = request.GET.get('q', '')
    current_user = request.user

    # Get all users that match the search query
    all_users = Profile.objects.filter(
        Q(user__username__icontains=query) |  # Search by username
        Q(user__email__icontains=query) |     # Search by email
        Q(phone__icontains=query)             # Search by phone number
    ).exclude(user=current_user)  # Exclude the current user
    
    # Get connected users (users with accepted connections)
    connected_user_ids = set()
    accepted_connections = ConnectionRequest.objects.filter(
        Q(sender=current_user, is_accepted=True) | 
        Q(receiver=current_user, is_accepted=True)
    )
    
    for connection in accepted_connections:
        if connection.sender == current_user:
            connected_user_ids.add(connection.receiver.id)
        else:
            connected_user_ids.add(connection.sender.id)
    
    # Get users with similar attributes
    similar_user_ids = set()
    
    # Get users with similar email domains
    if '@' in query:
        email_domain = query.split('@')[1]
        similar_email_users = User.objects.filter(
            email__icontains=email_domain
        ).exclude(id=current_user.id)
        for user in similar_email_users:
            similar_user_ids.add(user.id)
    
    # Get users with similar phone numbers (if phone numbers are in the same area code)
    if query.isdigit() and len(query) >= 3:
        area_code = query[:3]  # Assuming first 3 digits are area code
        similar_phone_users = User.objects.filter(
            profile__phone__startswith=area_code
        ).exclude(id=current_user.id)
        for user in similar_phone_users:
            similar_user_ids.add(user.id)
    
    # Get users with similar usernames
    if len(query) >= 3:
        username_prefix = query[:3]  # First 3 characters of query
        similar_username_users = User.objects.filter(
            username__startswith=username_prefix
        ).exclude(id=current_user.id)
        for user in similar_username_users:
            similar_user_ids.add(user.id)
    
    # Split users into connected, similar, and other
    connected_users = all_users.filter(user_id__in=connected_user_ids)
    similar_users = all_users.filter(user_id__in=similar_user_ids).exclude(user_id__in=connected_user_ids)
    other_users = all_users.exclude(user_id__in=connected_user_ids).exclude(user_id__in=similar_user_ids)
    
    # Combine the lists with connected users first, then similar users, then others
    users = list(connected_users) + list(similar_users) + list(other_users)
    
    # Prepare the suggestions data
    suggestions = []
    for user in users[:10]:  # Limit to 10 suggestions
        suggestions.append({
            'username': user.user.username,
            'email': user.user.email,
            'phone': user.phone,
            'is_connected': user.user.id in connected_user_ids,
            'is_similar': user.user.id in similar_user_ids
        })
    
    return JsonResponse({'suggestions': suggestions})
