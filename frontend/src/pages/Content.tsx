import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/services/api'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

interface ContentItem {
  id: string
  type: string
  title: string
  body: string
  status: string
  created_at: string
  updated_at: string
}

export default function Content() {
  const [showNewContentDialog, setShowNewContentDialog] = useState(false)
  const [selectedContent, setSelectedContent] = useState<ContentItem | null>(null)
  const [filter, setFilter] = useState<string>('all')

  const queryClient = useQueryClient()

  const { data: contentList, isLoading } = useQuery<ContentItem[]>({
    queryKey: ['content'],
    queryFn: async () => {
      const response = await api.get('/content')
      return response.data
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/content/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content'] })
    },
  })

  const filteredContent =
    contentList?.filter((item) => {
      if (filter === 'all') return true
      return item.type === filter
    }) || []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Content</h1>
          <p className="text-muted-foreground">
            AI-powered content generation and management
          </p>
        </div>
        <Button onClick={() => setShowNewContentDialog(true)}>
          + Generate Content
        </Button>
      </div>

      {/* Filters */}
      <div className="flex gap-2">
        <button
          onClick={() => setFilter('all')}
          className={`rounded-md px-3 py-1.5 text-sm ${
            filter === 'all'
              ? 'bg-primary text-primary-foreground'
              : 'bg-secondary text-secondary-foreground'
          }`}
        >
          All
        </button>
        <button
          onClick={() => setFilter('blog_post')}
          className={`rounded-md px-3 py-1.5 text-sm ${
            filter === 'blog_post'
              ? 'bg-primary text-primary-foreground'
              : 'bg-secondary text-secondary-foreground'
          }`}
        >
          Blog Posts
        </button>
        <button
          onClick={() => setFilter('email')}
          className={`rounded-md px-3 py-1.5 text-sm ${
            filter === 'email'
              ? 'bg-primary text-primary-foreground'
              : 'bg-secondary text-secondary-foreground'
          }`}
        >
          Emails
        </button>
        <button
          onClick={() => setFilter('social_post')}
          className={`rounded-md px-3 py-1.5 text-sm ${
            filter === 'social_post'
              ? 'bg-primary text-primary-foreground'
              : 'bg-secondary text-secondary-foreground'
          }`}
        >
          Social Media
        </button>
        <button
          onClick={() => setFilter('video_script')}
          className={`rounded-md px-3 py-1.5 text-sm ${
            filter === 'video_script'
              ? 'bg-primary text-primary-foreground'
              : 'bg-secondary text-secondary-foreground'
          }`}
        >
          Video Scripts
        </button>
      </div>

      {/* Content List */}
      {isLoading ? (
        <div className="flex h-96 items-center justify-center">
          <div className="text-center">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent"></div>
            <p className="mt-4 text-muted-foreground">Loading content...</p>
          </div>
        </div>
      ) : filteredContent.length === 0 ? (
        <Card className="p-12 text-center">
          <p className="text-muted-foreground">
            No content yet. Generate your first piece of content!
          </p>
          <Button className="mt-4" onClick={() => setShowNewContentDialog(true)}>
            Get Started
          </Button>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredContent.map((content) => (
            <Card key={content.id} className="p-6">
              <div className="space-y-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs ${
                          content.type === 'blog_post'
                            ? 'bg-blue-100 text-blue-700'
                            : content.type === 'email'
                            ? 'bg-green-100 text-green-700'
                            : content.type === 'social_post'
                            ? 'bg-purple-100 text-purple-700'
                            : 'bg-orange-100 text-orange-700'
                        }`}
                      >
                        {content.type.replace('_', ' ')}
                      </span>
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs ${
                          content.status === 'published'
                            ? 'bg-green-100 text-green-700'
                            : content.status === 'draft'
                            ? 'bg-gray-100 text-gray-700'
                            : 'bg-yellow-100 text-yellow-700'
                        }`}
                      >
                        {content.status}
                      </span>
                    </div>
                    <h3 className="mt-2 font-semibold">{content.title}</h3>
                    <p className="mt-1 line-clamp-2 text-sm text-muted-foreground">
                      {content.body.substring(0, 100)}...
                    </p>
                  </div>
                </div>

                <div className="text-xs text-muted-foreground">
                  Created {new Date(content.created_at).toLocaleDateString()}
                </div>

                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setSelectedContent(content)}
                    className="flex-1"
                  >
                    View
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      if (
                        confirm('Are you sure you want to delete this content?')
                      ) {
                        deleteMutation.mutate(content.id)
                      }
                    }}
                    className="flex-1"
                  >
                    Delete
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Generate Content Dialog */}
      {showNewContentDialog && (
        <NewContentDialog onClose={() => setShowNewContentDialog(false)} />
      )}

      {/* View Content Dialog */}
      {selectedContent && (
        <ViewContentDialog
          content={selectedContent}
          onClose={() => setSelectedContent(null)}
        />
      )}
    </div>
  )
}

function NewContentDialog({ onClose }: { onClose: () => void }) {
  const [contentType, setContentType] = useState('blog_post')
  const [prompt, setPrompt] = useState('')
  const queryClient = useQueryClient()

  const generateMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post('/content/generate', {
        type: contentType,
        prompt,
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content'] })
      onClose()
    },
  })

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <Card className="w-full max-w-2xl p-6">
        <h2 className="text-2xl font-bold">Generate AI Content</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Use Claude AI to generate high-quality content for your campaigns
        </p>

        <div className="mt-6 space-y-4">
          <div>
            <Label>Content Type</Label>
            <select
              value={contentType}
              onChange={(e) => setContentType(e.target.value)}
              className="mt-1.5 w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="blog_post">Blog Post</option>
              <option value="email">Email</option>
              <option value="social_post">Social Media Post</option>
              <option value="video_script">Video Script</option>
            </select>
          </div>

          <div>
            <Label>Prompt</Label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe what you want to generate... (e.g., 'Write a review for a keto diet product highlighting its benefits')"
              className="mt-1.5 min-h-32 w-full rounded-md border border-input bg-background px-3 py-2"
            />
          </div>
        </div>

        <div className="mt-6 flex gap-3">
          <Button onClick={onClose} variant="outline" className="flex-1">
            Cancel
          </Button>
          <Button
            onClick={() => generateMutation.mutate()}
            disabled={!prompt || generateMutation.isPending}
            className="flex-1"
          >
            {generateMutation.isPending ? 'Generating...' : 'Generate Content'}
          </Button>
        </div>
      </Card>
    </div>
  )
}

function ViewContentDialog({
  content,
  onClose,
}: {
  content: ContentItem
  onClose: () => void
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <Card className="max-h-[90vh] w-full max-w-4xl overflow-y-auto p-6">
        <div className="mb-6 flex items-start justify-between">
          <div>
            <h2 className="text-2xl font-bold">{content.title}</h2>
            <div className="mt-2 flex gap-2">
              <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs text-blue-700">
                {content.type.replace('_', ' ')}
              </span>
              <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-700">
                {content.status}
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-2xl text-muted-foreground hover:text-foreground"
          >
            ×
          </button>
        </div>

        <div className="prose max-w-none">
          <div className="whitespace-pre-wrap rounded-md bg-muted p-4">
            {content.body}
          </div>
        </div>

        <div className="mt-6 flex gap-3">
          <Button variant="outline" onClick={onClose} className="flex-1">
            Close
          </Button>
          <Button className="flex-1">Publish</Button>
        </div>
      </Card>
    </div>
  )
}
