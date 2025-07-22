from rest_framework import serializers
from customer.models import Customer, Address


class AddressCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = ['user', 'is_deleted']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)



class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = ['is_deleted', 'user']
        read_only_fields = ('user',)



class CustomerSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)
    
    class Meta:
        model = Customer
        exclude = ['is_deleted']
        read_only_fields = ['id', 'username', 'email', 'is_seller']




class CustomerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'phone', 'is_seller', 'picture']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return Customer.objects.create_user(**validated_data)
