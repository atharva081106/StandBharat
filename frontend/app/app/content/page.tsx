'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { useAppProvider } from '@/lib/providers'
import { ApiClient } from '@/lib/api/client'

export default function Content() {
  const { auth } = useAppProvider()
  const { activeBrand } = auth
  const [drafts, setDrafts] = useState<any[]>([])
  const [publications, setPublications] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      if (!activeBrand) return
      setLoading(true)
      try {
        const [draftsData, pubsData] = await Promise.all([
          ApiClient.get<any[]>('/api/content/drafts'),
          ApiClient.get<any[]>('/api/publications')
        ])
        setDrafts(draftsData || [])
        setPublications(pubsData || [])
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [activeBrand])

  const mergedContent = drafts.map(draft => {
    const pub = publications.find(p => p.content_draft_id === draft.id)
    return {
      ...draft,
      status: pub ? pub.status : (draft.status || 'DRAFT'),
      platform: pub ? pub.platform : null,
      error_message: pub ? pub.error_message : null,
      published_at: pub ? pub.published_at : null
    }
  })

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[var(--color-border-primary)] pb-6">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight text-[var(--color-text-primary)]">Content Studio</h1>
          <p className="text-[var(--color-text-tertiary)] text-lg mt-1">All AI-generated and human marketing content in one place.</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" className="hidden sm:inline-flex">Filter</Button>
          <Button>+ New Content</Button>
        </div>
      </div>
      
      <div className="bg-[var(--color-bg-surface)] border border-[var(--color-border-primary)] rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left whitespace-nowrap">
            <thead className="bg-[var(--color-bg-subtle)] text-[var(--color-text-muted)] border-b border-[var(--color-border-primary)] text-xs uppercase tracking-wider font-semibold">
              <tr>
                <th className="px-6 py-4">Title</th>
                <th className="px-6 py-4">Type</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Platform</th>
                <th className="px-6 py-4 text-right">Updated</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--color-border-primary)]">
              {mergedContent.map((item) => (
                <tr
                  key={item.id}
                  onClick={() => { window.location.href = `/app/content/${item.id}` }}
                  className="hover:bg-[var(--color-bg-subtle)] transition-colors cursor-pointer"
                >
                  <td className="px-6 py-4">
                    <span className="font-semibold text-[var(--color-text-primary)]">{item.title}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-[var(--color-text-secondary)]">{item.content_type}</span>
                  </td>
                  <td className="px-6 py-4">
                    <Badge variant={item.status === 'PUBLISHED' ? 'success' : item.status === 'FAILED' ? 'danger' : item.status === 'DRAFT' ? 'warning' : 'secondary'} className="text-[10px] uppercase tracking-wider">
                      {item.status}
                    </Badge>
                    {item.status === 'FAILED' && <div className="text-xs text-red-500 mt-1">{item.error_message}</div>}
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-[var(--color-text-secondary)] capitalize">{item.platform || '—'}</span>
                  </td>
                  <td className="px-6 py-4 text-right text-[var(--color-text-tertiary)]">
                    {new Date(item.updated_at).toLocaleDateString()}
                    {item.published_at && <div className="text-xs">Published: {new Date(item.published_at).toLocaleString()}</div>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {!loading && mergedContent.length === 0 && (
          <div className="flex flex-col items-center justify-center py-16 text-center px-4">
            <p className="text-[var(--color-text-primary)] font-medium">No content yet</p>
            <p className="text-sm text-[var(--color-text-tertiary)] mt-1">Create your first piece of content to get started.</p>
            <Button variant="outline" className="mt-4">Create Content</Button>
          </div>
        )}
        {loading && (
          <div className="flex flex-col items-center justify-center py-16 text-center px-4 text-[#A9A4A0]">
            Loading content...
          </div>
        )}
      </div>
    </div>
  )
}
