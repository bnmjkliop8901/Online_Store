from rest_framework import serializers
from customer.models import Customer, Address


class AddressCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = ['user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)



class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ('user',)



class CustomerSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'phone', 'addresses'
        ]
        read_only_fields = ['id']



class CustomerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'phone', 'is_seller', 'picture']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return Customer.objects.create_user(**validated_data)
