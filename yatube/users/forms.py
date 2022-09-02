from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


# создаем класс формы, наследуемый от класса UserCreationForm
class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        # связываем класс формы с моделью User
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
