
from pathlib import Path

from amocrm.v2.entity.contact import Contact
from amocrm.v2.entity.user import User
from amocrm.v2.entity.company import Company
from amocrm.v2.entity.pipeline import Pipeline, Status
from amocrm.v2.entity.lead import Lead

from amocrm.v2 import tokens
tokens.default_token_manager(
    client_id="443850d2-f019-4671-aced-ef3c42991c37",
    client_secret="ld7IMMbxvxQIy8JIKlf2onGBXSVg6NNlmqITtF1GEkbk1QjLRgScY0mdTG3UaznX",
    subdomain="amocrm3yopmailcom",
    redirect_url="http://tests.com",
    storage=tokens.FileTokensStorage(directory_path=str(Path.home())),
)
# tokens.default_token_manager.init("def50200e9a4fe5a30712e3c6aa6936331e98869a6d55789dcf06d44a89b20a3a45229161d42d74413e6794b1f3074a3fd242d8c46c186f27ce07d59161f0e9d71f5ae68ff7c1ca564554bca93095c7781578ba8a99739c232b924a243c1d3067866a2f1c791fd4511d907df65c4dfc31a237ed5d631b810d91152d7c92e9fea62f7c34ffc377ef672beb3cc2a80d3a30eaed7a68793dffd7abcfb4b57376f9c2b51d4681c77bcaa17e7ec11aa73f0a2285498d6a8b4c4d04b919af81cba422fd27c405867ff294e6bc6895d4bd37cbaef26a0ff6531987125c2c087ce287142b8aecca7a727b337c6807ab1d3bfb41a26a5510175a9222798fa2248e3d9e057085e9a0aaa0521455325ec9fd2364c06a83c0b41fd8e3d072eb3df6515fe8289a12f3ace764bf60736308af367c45b4b1c8bc674e6b73c31a058722ef3947b1b17ab14d3dab6bf7763f6276e797afbd2245157aac82a574e5b94ad656e123635250f8e4510d9a9305f2f7e8cf9576bddd09e93600546ec799c17091d4d34773fd04ffdb74a691af3a33e063becd341000cb5ffe2f44ff781611ac7e4c877876f6e612926dde7cef0a8f6c1a482dafd1ba47f2c652a6b2a098cac", skip_error=True)

# c = Contact.objects.get(query="First")
# c.company = Company.objects.get(query="New")
# print(list(Pipeline.objects.all()))
p = list(Pipeline.objects.all())[0]
p.name = "ВТОРАЯ"
p.save()
# print(list(c.leads)

# status = Status.get_for(list(c.leads)[0].pipeline).get(query="принимают решение")
# print(status)
# lead = Lead.objects.get(query="test")
# lead.tags.add("test")
# print(lead.status)
# lead.status = "переговоры"
# lead.save()
# c.leads.add(lead)
# c.tags.remove("tag")
# c.save()

# print(c.name)
# print(c.created_at)
# print(list(c.tags))