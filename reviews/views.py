from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from .forms import ReviewForm
import datetime
from django.contrib.auth.decorators import login_required
from .models import Review, Book, Cluster
from django.contrib.auth.models import User
from .suggestions import update_clusters
# Create your views here.


def review_list(request):
	latest_review_list = Review.objects.order_by('-pub_date')[:9]
	context = {'latest_review_list': latest_review_list}
	return render(request, 'reviews/review_list.html', context)

def review_detail(request, review_id):
	review = get_object_or_404(Review, pk = review_id)
	return render(request, 'reviews/review_detail.html', {'review': review})

def book_list(request):
	book_list = Book.objects.order_by('-name')
	context = {'book_list': book_list }
	return render(request, 'reviews/book_list.html', context)

def book_detail(request, book_id):
	book = get_object_or_404(Book, pk = book_id)
	form = ReviewForm()
	return render(request, 'reviews/book_detail.html', {'book': book, 'form': form})

@login_required
def add_review(request, book_id):
	book = get_object_or_404(Book, pk = book_id)
	form = ReviewForm(request.POST)
	if form.is_valid():
		rating = form.cleaned_data['rating']
		comment = form.cleaned_data['comment']
		user_name = request.user.username
		review = Review()
		review.book = book
		review.rating = rating
		review.comment = comment
		review.user_name = user_name
		review.pub_date = datetime.datetime.now()
		review.save()
		update_clusters()
		# Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('reviews:book_detail', args=(book_id,)))

	return render(request, 'reviews/book_detail.html', {'book': book, 'form': form})

def user_review_list(request, username=None):
	if not username:
		username = request.user.username
	latest_review_list = Review.objects.filter(user_name=username).order_by('-pub_date')
	context = {'latest_review_list': latest_review_list, 'username': username}
	return render(request, 'reviews/user_review_list.html', context)

@login_required
def user_recommendation_list(request):
	#get the user reviews
	user_reviews = Review.objects.filter(user_name=request.user.username).prefetch_related('book')
	#from the reviews get a set of book IDs
	user_reviews_book_ids = set(map(lambda x: x.book.id, user_reviews))
	#get the request user's cluster (the first one for now)
	try:
		user_cluster_name = User.objects.get(username=request.user.username).cluster_set.first().name
	except:		#if user has not been asigned to a cluster, then update and assign
		update_clusters()
		user_cluster_name = User.objects.get(username=request.user.username).cluster_set.first().name

	#get usernames for other members of the cluster
	user_cluster_others = Cluster.objects.get(name=user_cluster_name).users.exclude(username=request.user.username).all()
	other_member_usernames = set(map(lambda x:x.username, user_cluster_others))

	#get other members reviews excluding request users reviewed books
	other_users_reviews = Review.objects.filter(user_name__in=other_member_usernames)\
	.exclude(book_id__in=user_reviews_book_ids)
	other_user_reviews_book_ids = set(map(lambda x: x.book_id, other_users_reviews))

	# then get a book list order by rating
	#book_list = Book.objects.exclude(id__in=user_reviews_book_ids)
	book_list = sorted(list(
		Book.objects.filter(id__in=other_user_reviews_book_ids)),
		key = lambda x: x.average_rating,
		reverse=True
		)
	return render(
		request,
		'reviews/user_recommendation_list.html',
		{'username': request.user.username, 'book_list': book_list}
	)