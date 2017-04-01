#   Copyright 2017 Maurice Carey
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#

from django.db import models

# Create your models here.


class PublicKey(models.Model):
    key = models.TextField()

    def __str__(self):
        return 'public_key: %s' % self.key


class PrivateKey(models.Model):
    key = models.TextField()

    def __str__(self):
        return 'private_key: %s' % self.key


class KeyPair(models.Model):
    private = models.ForeignKey(PrivateKey)
    public = models.ForeignKey(PublicKey)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'ID: %s, %s, %s' % (self.pk, self.private, self.public)
