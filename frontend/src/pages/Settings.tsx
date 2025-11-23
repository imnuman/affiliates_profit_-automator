import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/services/api'
import { useAuthStore } from '@/store/authStore'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

export default function Settings() {
  const [activeTab, setActiveTab] = useState('profile')

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground">Manage your account and preferences</p>
      </div>

      {/* Tabs */}
      <div className="border-b">
        <div className="flex gap-6">
          <button
            onClick={() => setActiveTab('profile')}
            className={`pb-3 text-sm font-medium ${
              activeTab === 'profile'
                ? 'border-b-2 border-primary text-primary'
                : 'text-muted-foreground'
            }`}
          >
            Profile
          </button>
          <button
            onClick={() => setActiveTab('subscription')}
            className={`pb-3 text-sm font-medium ${
              activeTab === 'subscription'
                ? 'border-b-2 border-primary text-primary'
                : 'text-muted-foreground'
            }`}
          >
            Subscription
          </button>
          <button
            onClick={() => setActiveTab('integrations')}
            className={`pb-3 text-sm font-medium ${
              activeTab === 'integrations'
                ? 'border-b-2 border-primary text-primary'
                : 'text-muted-foreground'
            }`}
          >
            Integrations
          </button>
          <button
            onClick={() => setActiveTab('api')}
            className={`pb-3 text-sm font-medium ${
              activeTab === 'api'
                ? 'border-b-2 border-primary text-primary'
                : 'text-muted-foreground'
            }`}
          >
            API Keys
          </button>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'profile' && <ProfileSettings />}
      {activeTab === 'subscription' && <SubscriptionSettings />}
      {activeTab === 'integrations' && <IntegrationsSettings />}
      {activeTab === 'api' && <APIKeysSettings />}
    </div>
  )
}

function ProfileSettings() {
  const user = useAuthStore((state) => state.user)
  const [fullName, setFullName] = useState(user?.full_name || '')
  const [email, setEmail] = useState(user?.email || '')
  const queryClient = useQueryClient()

  const updateProfileMutation = useMutation({
    mutationFn: async (data: { full_name: string; email: string }) => {
      const response = await api.put('/users/me', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user'] })
    },
  })

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <h3 className="mb-4 font-semibold">Personal Information</h3>
        <div className="space-y-4">
          <div>
            <Label htmlFor="fullName">Full Name</Label>
            <Input
              id="fullName"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="John Doe"
            />
          </div>
          <div>
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="john@example.com"
            />
          </div>
          <Button
            onClick={() =>
              updateProfileMutation.mutate({ full_name: fullName, email })
            }
            disabled={updateProfileMutation.isPending}
          >
            {updateProfileMutation.isPending ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="mb-4 font-semibold">Change Password</h3>
        <div className="space-y-4">
          <div>
            <Label htmlFor="currentPassword">Current Password</Label>
            <Input id="currentPassword" type="password" />
          </div>
          <div>
            <Label htmlFor="newPassword">New Password</Label>
            <Input id="newPassword" type="password" />
          </div>
          <div>
            <Label htmlFor="confirmPassword">Confirm New Password</Label>
            <Input id="confirmPassword" type="password" />
          </div>
          <Button>Update Password</Button>
        </div>
      </Card>
    </div>
  )
}

function SubscriptionSettings() {
  const user = useAuthStore((state) => state.user)

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <h3 className="mb-4 font-semibold">Current Plan</h3>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-2xl font-bold capitalize">{user?.tier || 'Starter'}</p>
            <p className="text-muted-foreground">
              Status: <span className="capitalize">{user?.status || 'Active'}</span>
            </p>
          </div>
          <Button variant="outline">Change Plan</Button>
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="mb-4 font-semibold">Available Plans</h3>
        <div className="grid gap-4 md:grid-cols-3">
          <PlanCard
            name="Starter"
            price="$49"
            features={[
              '50 AI content pieces/month',
              '5 campaigns',
              'Basic analytics',
              'Email support',
            ]}
            current={user?.tier === 'starter'}
          />
          <PlanCard
            name="Professional"
            price="$149"
            features={[
              '200 AI content pieces/month',
              '25 campaigns',
              'Advanced analytics',
              'Priority support',
              'WordPress integration',
              'Social media automation',
            ]}
            current={user?.tier === 'professional'}
            highlighted
          />
          <PlanCard
            name="Agency"
            price="$399"
            features={[
              'Unlimited AI content',
              'Unlimited campaigns',
              'Full analytics suite',
              '24/7 support',
              'All integrations',
              'White-label options',
              'Team collaboration',
            ]}
            current={user?.tier === 'agency'}
          />
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="mb-4 font-semibold">Billing History</h3>
        <div className="space-y-2">
          <div className="flex justify-between border-b pb-2">
            <span className="text-sm text-muted-foreground">No billing history yet</span>
          </div>
        </div>
      </Card>
    </div>
  )
}

function PlanCard({
  name,
  price,
  features,
  current,
  highlighted,
}: {
  name: string
  price: string
  features: string[]
  current?: boolean
  highlighted?: boolean
}) {
  return (
    <Card
      className={`p-6 ${highlighted ? 'border-primary ring-2 ring-primary' : ''}`}
    >
      <div className="mb-4">
        <h4 className="text-xl font-bold">{name}</h4>
        <p className="mt-2 text-3xl font-bold">{price}</p>
        <p className="text-sm text-muted-foreground">/month</p>
      </div>
      <ul className="mb-6 space-y-2">
        {features.map((feature, index) => (
          <li key={index} className="flex items-start gap-2 text-sm">
            <span className="text-green-600">✓</span>
            <span>{feature}</span>
          </li>
        ))}
      </ul>
      <Button className="w-full" disabled={current}>
        {current ? 'Current Plan' : 'Upgrade'}
      </Button>
    </Card>
  )
}

function IntegrationsSettings() {
  return (
    <div className="space-y-6">
      <Card className="p-6">
        <h3 className="mb-4 font-semibold">WordPress</h3>
        <p className="mb-4 text-sm text-muted-foreground">
          Connect your WordPress site to automatically publish content
        </p>
        <div className="space-y-4">
          <div>
            <Label>Site URL</Label>
            <Input placeholder="https://yoursite.com" />
          </div>
          <div>
            <Label>Username</Label>
            <Input placeholder="admin" />
          </div>
          <div>
            <Label>Application Password</Label>
            <Input type="password" />
          </div>
          <Button>Connect WordPress</Button>
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="mb-4 font-semibold">Social Media</h3>
        <div className="space-y-4">
          <IntegrationItem
            name="Twitter"
            description="Post to Twitter automatically"
            connected={false}
          />
          <IntegrationItem
            name="Facebook"
            description="Share content on Facebook pages"
            connected={false}
          />
          <IntegrationItem
            name="LinkedIn"
            description="Publish to LinkedIn profile"
            connected={false}
          />
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="mb-4 font-semibold">Email Marketing</h3>
        <div className="space-y-4">
          <IntegrationItem
            name="Mailchimp"
            description="Sync subscribers and send campaigns"
            connected={false}
          />
          <IntegrationItem
            name="SendGrid"
            description="Send emails via SendGrid"
            connected={false}
          />
        </div>
      </Card>
    </div>
  )
}

function IntegrationItem({
  name,
  description,
  connected,
}: {
  name: string
  description: string
  connected: boolean
}) {
  return (
    <div className="flex items-center justify-between rounded-lg border p-4">
      <div>
        <p className="font-medium">{name}</p>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
      <Button variant={connected ? 'outline' : 'default'}>
        {connected ? 'Disconnect' : 'Connect'}
      </Button>
    </div>
  )
}

function APIKeysSettings() {
  const [showNewKeyDialog, setShowNewKeyDialog] = useState(false)

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h3 className="font-semibold">API Keys</h3>
            <p className="text-sm text-muted-foreground">
              Manage API keys for programmatic access
            </p>
          </div>
          <Button onClick={() => setShowNewKeyDialog(true)}>Create New Key</Button>
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between rounded-lg border p-4">
            <div>
              <p className="font-mono text-sm">sk_test_**********************abc123</p>
              <p className="text-xs text-muted-foreground">
                Created on Jan 15, 2025 • Last used 2 days ago
              </p>
            </div>
            <Button variant="outline" size="sm">
              Revoke
            </Button>
          </div>

          <div className="rounded-lg border border-dashed p-8 text-center">
            <p className="text-muted-foreground">
              No API keys yet. Create one to get started.
            </p>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="mb-4 font-semibold">Webhooks</h3>
        <p className="mb-4 text-sm text-muted-foreground">
          Configure webhooks to receive real-time events
        </p>
        <Button variant="outline">Add Webhook</Button>
      </Card>
    </div>
  )
}
