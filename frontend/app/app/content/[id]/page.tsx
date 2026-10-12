"use client"

import React, { useState, useEffect, useCallback, use } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ApiClient } from '@/lib/api/client'
import { useAppProvider } from '@/lib/providers'
import {
  CheckCircle2,
  XCircle,
  AlertCircle,
  Clock,
  RefreshCw,
  Send,
  ArrowLeft,
  Share2,
  FileText,
  AlertTriangle,
  ExternalLink,
  ShieldAlert,
  History,
  RotateCcw,
  Check,
  Building
} from 'lucide-react'

interface ContentDraft {
  id: string
  content_project_id: string
  brief_id?: string | null
  workspace_id: string
  brand_id: string
  content_type?: string | null
  title: string
  body: string
  status: string
  generated_by?: string | null
  generation_metadata?: Record<string, any> | null
  created_at: string
  updated_at: string
}

interface ContentApproval {
  id: string
  content_project_id: string
  content_draft_id: string
  workspace_id: string
  brand_id: string
  requested_by: string
  reviewed_by?: string | null
  status: string
  review_comment?: string | null
  created_at: string
  reviewed_at?: string | null
}

interface PublicationAttempt {
  id: string
  publication_id: string
  attempt_number: string
  status: string
  request_metadata?: Record<string, any> | null
  response_metadata?: Record<string, any> | null
  error_code?: string | null
  error_message?: string | null
  started_at: string
  completed_at?: string | null
}

interface Publication {
  id: string
  workspace_id: string
  brand_id: string
  content_project_id: string
  content_draft_id: string
  platform: string
  status: string
  external_post_id?: string | null
  published_at?: string | null
  scheduled_for?: string | null
  error_code?: string | null
  error_message?: string | null
  idempotency_key: string
  created_by: string
  created_at: string
  updated_at: string
  attempts?: PublicationAttempt[]
}

interface PublisherConnection {
  platform: string
  status: string
  external_account_name?: string | null
}

export default function ContentDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params)
  const draftId = resolvedParams.id

  const { auth } = useAppProvider()
  const { activeBrand } = auth

  const [draft, setDraft] = useState<ContentDraft | null>(null)
  const [approvals, setApprovals] = useState<ContentApproval[]>([])
  const [publication, setPublication] = useState<Publication | null>(null)
  const [publishers, setPublishers] = useState<PublisherConnection[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Interactive UI states
  const [actionLoading, setActionLoading] = useState(false)
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
  const [selectedPlatform, setSelectedPlatform] = useState<string>('linkedin')
  const [rejecting, setRejecting] = useState(false)
  const [rejectComment, setRejectComment] = useState('')

  // Reconciliation modal state
  const [reconciling, setReconciling] = useState(false)
  const [reconcileResolution, setReconcileResolution] = useState<'PUBLISHED' | 'FAILED' | 'RETRY'>('PUBLISHED')
  const [reconcileExternalId, setReconcileExternalId] = useState('')
  const [reconcileNotes, setReconcileNotes] = useState('')

  const fetchDetails = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      // 1. Fetch Draft
      const draftData = await ApiClient.get<ContentDraft>(`/api/content/drafts/${draftId}`)
      setDraft(draftData)

      // 2. Fetch Approvals
      try {
        const approvalsData = await ApiClient.get<ContentApproval[]>('/api/approvals')
        const filteredApprovals = (approvalsData || []).filter(a => a.content_draft_id === draftId)
        setApprovals(filteredApprovals)
      } catch (e) {
        console.warn('Approvals fetch error', e)
      }

      // 3. Fetch Publications
      try {
        const pubsData = await ApiClient.get<Publication[]>('/api/publications')
        const pub = (pubsData || []).find(p => p.content_draft_id === draftId)
        if (pub) {
          // Fetch detailed publication with attempts
          try {
            const detailedPub = await ApiClient.get<Publication>(`/api/publications/${pub.id}`)
            setPublication(detailedPub)
          } catch (e) {
            setPublication(pub)
          }
        } else {
          setPublication(null)
        }
      } catch (e) {
        console.warn('Publications fetch error', e)
      }

      // 4. Fetch Publisher Connections
      try {
        const pubsConnections = await ApiClient.get<PublisherConnection[]>('/api/publishers')
        setPublishers(pubsConnections || [])
        const connectedPlatforms = (pubsConnections || []).filter(c => c.status === 'CONNECTED')
        if (connectedPlatforms.length > 0) {
          setSelectedPlatform(connectedPlatforms[0].platform)
        }
      } catch (e) {
        console.warn('Publisher connections fetch error', e)
      }
    } catch (err: any) {
      console.error('Failed to load content details:', err)
      setError(err.message || 'Content draft not found.')
    } finally {
      setLoading(false)
    }
  }, [draftId])

  useEffect(() => {
    fetchDetails()
  }, [fetchDetails, activeBrand])

  // Submit for Review
  const handleSubmitReview = async () => {
    if (!draft) return
    setActionLoading(true)
    setFeedback(null)
    try {
      await ApiClient.post(`/api/approvals/projects/${draft.content_project_id}/submit-review`, {
        content_draft_id: draft.id
      })
      setFeedback({ type: 'success', text: 'Draft submitted for formal review.' })
      await fetchDetails()
    } catch (err: any) {
      setFeedback({ type: 'error', text: err.message || 'Failed to submit for review.' })
    } finally {
      setActionLoading(false)
    }
  }

  // Approve content
  const handleApprove = async (approvalId: string) => {
    setActionLoading(true)
    setFeedback(null)
    try {
      await ApiClient.post(`/api/approvals/${approvalId}/approve`, {})
      setFeedback({ type: 'success', text: 'Approval granted: Content is now officially APPROVED.' })
      await fetchDetails()
    } catch (err: any) {
      setFeedback({ type: 'error', text: err.message || 'Failed to approve draft.' })
    } finally {
      setActionLoading(false)
    }
  }

  // Reject content
  const handleReject = async (approvalId: string) => {
    setActionLoading(true)
    setFeedback(null)
    try {
      await ApiClient.post(`/api/approvals/${approvalId}/reject`, {
        review_comment: rejectComment.trim() || 'Rejected during review.'
      })
      setFeedback({ type: 'success', text: 'Draft rejected.' })
      setRejecting(false)
      setRejectComment('')
      await fetchDetails()
    } catch (err: any) {
      setFeedback({ type: 'error', text: err.message || 'Failed to reject draft.' })
    } finally {
      setActionLoading(false)
    }
  }

  // Publish / Retry Publish
  const handlePublish = async () => {
    if (!draft) return
    setActionLoading(true)
    setFeedback(null)
    try {
      const pub = await ApiClient.post<Publication>(
        `/api/content/drafts/${draft.id}/publish?platform=${selectedPlatform}`,
        {}
      )
      setPublication(pub)
      setFeedback({
        type: 'success',
        text: `Publication dispatched: Status is now ${pub.status}.`
      })
      await fetchDetails()
    } catch (err: any) {
      setFeedback({ type: 'error', text: err.message || 'Failed to publish draft.' })
    } finally {
      setActionLoading(false)
    }
  }

  // Reconcile Publication
  const handleReconcile = async () => {
    if (!publication) return
    setActionLoading(true)
    setFeedback(null)
    try {
      const result = await ApiClient.post<Publication>(`/api/publications/${publication.id}/reconcile`, {
        resolution: reconcileResolution,
        external_post_id: reconcileResolution === 'PUBLISHED' ? reconcileExternalId : undefined,
        notes: reconcileNotes.trim() || undefined
      })
      setPublication(result)
      setFeedback({
        type: 'success',
        text: `Publication reconciled successfully. Current status: ${result.status}.`
      })
      setReconciling(false)
      setReconcileExternalId('')
      setReconcileNotes('')
      await fetchDetails()
    } catch (err: any) {
      setFeedback({ type: 'error', text: err.message || 'Reconciliation failed.' })
    } finally {
      setActionLoading(false)
    }
  }

  // Helper status badge for drafts
  const getDraftStatusBadge = (status: string) => {
    switch (status) {
      case 'APPROVED':
        return <Badge variant="success" className="py-1 px-2.5 font-medium">APPROVED</Badge>
      case 'IN_REVIEW':
        return <Badge variant="warning" className="py-1 px-2.5 font-medium">IN REVIEW</Badge>
      case 'REJECTED':
        return <Badge variant="danger" className="py-1 px-2.5 font-medium">REJECTED</Badge>
      case 'CHANGES_REQUESTED':
        return <Badge variant="secondary" className="py-1 px-2.5 font-medium">CHANGES REQUESTED</Badge>
      case 'PUBLISHED':
        return <Badge variant="success" className="py-1 px-2.5 font-medium">PUBLISHED</Badge>
      default:
        return <Badge variant="outline" className="py-1 px-2.5 font-medium">{status}</Badge>
    }
  }

  // Helper status badge for publications
  const getPubStatusBadge = (status: string) => {
    switch (status) {
      case 'PUBLISHED':
        return <Badge variant="success" className="py-1 px-2.5 font-mono">PUBLISHED</Badge>
      case 'PUBLISHING':
        return <Badge variant="secondary" className="py-1 px-2.5 font-mono animate-pulse">PUBLISHING</Badge>
      case 'QUEUED':
        return <Badge variant="warning" className="py-1 px-2.5 font-mono">QUEUED</Badge>
      case 'FAILED':
        return <Badge variant="danger" className="py-1 px-2.5 font-mono">FAILED</Badge>
      case 'BLOCKED':
        return <Badge variant="danger" className="py-1 px-2.5 font-mono">BLOCKED</Badge>
      case 'RECONCILIATION_REQUIRED':
        return <Badge variant="danger" className="py-1 px-2.5 font-mono bg-amber-600 text-white">RECONCILIATION_REQUIRED</Badge>
      default:
        return <Badge variant="outline" className="py-1 px-2.5 font-mono">{status}</Badge>
    }
  }

  // Find latest active approval
  const latestApproval = approvals.length > 0 ? approvals[0] : null
  const isApproved = latestApproval?.status === 'APPROVED' || draft?.status === 'APPROVED'
  const isPendingApproval = latestApproval?.status === 'PENDING' || draft?.status === 'IN_REVIEW'
  const connectedPlatforms = publishers.filter(p => p.status === 'CONNECTED')

  if (loading) {
    return (
      <div className="space-y-6 max-w-6xl mx-auto py-8">
        <div className="h-6 w-32 bg-[var(--color-bg-subtle)] rounded animate-pulse"></div>
        <div className="h-10 w-2/3 bg-[var(--color-bg-subtle)] rounded animate-pulse"></div>
        <Card className="animate-pulse bg-[var(--color-bg-surface)] border-[var(--color-border-primary)]">
          <CardContent className="p-8 space-y-4">
            <div className="h-4 bg-[var(--color-bg-subtle)] rounded w-full"></div>
            <div className="h-4 bg-[var(--color-bg-subtle)] rounded w-5/6"></div>
            <div className="h-4 bg-[var(--color-bg-subtle)] rounded w-4/6"></div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error || !draft) {
    return (
      <div className="max-w-3xl mx-auto py-16 text-center space-y-6">
        <div className="w-16 h-16 rounded-2xl bg-red-50 dark:bg-red-950/40 text-red-600 dark:text-red-400 flex items-center justify-center mx-auto shadow-sm">
          <AlertCircle className="w-8 h-8" />
        </div>
        <div className="space-y-2">
          <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">Draft Not Found</h1>
          <p className="text-sm text-[var(--color-text-tertiary)] max-w-md mx-auto">
            {error || `No content draft exists with ID ${draftId} in the selected workspace.`}
          </p>
        </div>
        <Link href="/app/content">
          <Button variant="outline" className="flex items-center gap-2 mx-auto">
            <ArrowLeft className="w-4 h-4" /> Back to Content Studio
          </Button>
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-16">
      {/* Top Navigation */}
      <div className="flex items-center justify-between">
        <Link
          href="/app/content"
          className="inline-flex items-center gap-2 text-sm text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)] transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Content Studio
        </Link>
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={fetchDetails}
            disabled={actionLoading}
            className="flex items-center gap-2"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${actionLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Link href="/app/approvals">
            <Button variant="outline" size="sm">
              Approvals Queue
            </Button>
          </Link>
        </div>
      </div>

      {/* Global Feedback Banner */}
      {feedback && (
        <div
          className={`p-4 rounded-xl border flex items-center justify-between text-sm ${
            feedback.type === 'success'
              ? 'bg-emerald-50/80 border-emerald-200 text-emerald-800 dark:bg-emerald-950/40 dark:border-emerald-800 dark:text-emerald-300'
              : 'bg-red-50/80 border-red-200 text-red-800 dark:bg-red-950/40 dark:border-red-800 dark:text-red-300'
          }`}
        >
          <div className="flex items-center gap-2">
            {feedback.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 shrink-0" />
            )}
            <span>{feedback.text}</span>
          </div>
          <button
            onClick={() => setFeedback(null)}
            className="text-xs font-semibold hover:underline ml-4"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Header and Quick Actions */}
      <div className="flex flex-col md:flex-row md:items-start justify-between gap-6 border-b border-[var(--color-border-primary)] pb-6">
        <div className="space-y-3 flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-3xl font-semibold tracking-tight text-[var(--color-text-primary)]">
              {draft.title}
            </h1>
            {getDraftStatusBadge(draft.status)}
            {draft.content_type && (
              <Badge variant="secondary" className="font-mono text-xs uppercase tracking-wider">
                {draft.content_type}
              </Badge>
            )}
          </div>
          <div className="flex flex-wrap items-center gap-4 text-xs text-[var(--color-text-muted)]">
            <span>Draft ID: <code className="font-mono">{draft.id.slice(0, 8)}...</code></span>
            <span>Created: {new Date(draft.created_at).toLocaleString()}</span>
            <span>Updated: {new Date(draft.updated_at).toLocaleString()}</span>
          </div>
        </div>

        {/* Dynamic Header Actions based on approval state */}
        <div className="flex flex-wrap items-center gap-3 shrink-0">
          {/* If In Review and user can approve */}
          {isPendingApproval && latestApproval && (
            <>
              <Button
                variant="outline"
                disabled={actionLoading}
                onClick={() => setRejecting(!rejecting)}
                className="text-red-600 border-red-200 hover:bg-red-50 dark:hover:bg-red-950/30"
              >
                Reject
              </Button>
              <Button
                disabled={actionLoading}
                onClick={() => handleApprove(latestApproval.id)}
                className="bg-emerald-600 hover:bg-emerald-700 text-white flex items-center gap-1.5"
              >
                <CheckCircle2 className="w-4 h-4" />
                {actionLoading ? 'Approving...' : 'Approve Draft'}
              </Button>
            </>
          )}

          {/* If not submitted for review yet */}
          {!isPendingApproval && !isApproved && (
            <Button
              disabled={actionLoading}
              onClick={handleSubmitReview}
              className="bg-[var(--color-accent)] hover:opacity-90 text-white flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
              {actionLoading ? 'Submitting...' : 'Submit for Review'}
            </Button>
          )}
        </div>
      </div>

      {/* Inline Reject Form */}
      {rejecting && latestApproval && (
        <Card className="border-red-200 bg-red-50/40 dark:bg-red-950/20">
          <CardContent className="p-5 space-y-3">
            <h4 className="text-sm font-semibold text-red-900 dark:text-red-200">
              Provide Rejection Feedback
            </h4>
            <textarea
              rows={2}
              value={rejectComment}
              onChange={e => setRejectComment(e.target.value)}
              placeholder="Explain why this draft is being rejected..."
              className="w-full text-sm p-3 rounded-lg border border-red-200 dark:border-red-800 bg-white dark:bg-black/40 text-[var(--color-text-primary)]"
            />
            <div className="flex justify-end gap-2">
              <Button variant="outline" size="sm" onClick={() => setRejecting(false)}>
                Cancel
              </Button>
              <Button
                size="sm"
                disabled={actionLoading}
                onClick={() => handleReject(latestApproval.id)}
                className="bg-red-600 hover:bg-red-700 text-white"
              >
                {actionLoading ? 'Rejecting...' : 'Confirm Rejection'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Grid: Draft Content on Left (2/3), Publishing & Approval Pipeline on Right (1/3) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Draft Content & Generation Details */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="border-[var(--color-border-primary)] bg-[var(--color-bg-surface)]">
            <CardHeader className="border-b border-[var(--color-border-primary)] py-4 px-6 flex flex-row items-center justify-between">
              <CardTitle className="text-base font-semibold flex items-center gap-2">
                <FileText className="w-4 h-4 text-[var(--color-accent)]" /> Content Body
              </CardTitle>
              <span className="text-xs text-[var(--color-text-muted)] font-mono">
                {draft.body.length} characters
              </span>
            </CardHeader>
            <CardContent className="p-6">
              <div className="whitespace-pre-wrap font-serif text-[var(--color-text-primary)] text-base leading-relaxed bg-[var(--color-bg-subtle)] p-6 rounded-xl border border-[var(--color-border-primary)]">
                {draft.body}
              </div>
            </CardContent>
          </Card>

          {/* AI Generation Context (if available) */}
          {draft.generation_metadata && (
            <Card className="border-[var(--color-border-primary)] bg-[var(--color-bg-surface)]">
              <CardHeader className="py-3 px-6 border-b border-[var(--color-border-primary)]">
                <CardTitle className="text-xs uppercase tracking-wider font-semibold text-[var(--color-text-muted)]">
                  Generation Metadata
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4 font-mono text-xs bg-[var(--color-bg-base)] overflow-x-auto text-[var(--color-text-secondary)]">
                <pre>{JSON.stringify(draft.generation_metadata, null, 2)}</pre>
              </CardContent>
            </Card>
          )}

          {/* Approval History Timeline */}
          <Card className="border-[var(--color-border-primary)] bg-[var(--color-bg-surface)]">
            <CardHeader className="border-b border-[var(--color-border-primary)] py-4 px-6">
              <CardTitle className="text-base font-semibold flex items-center gap-2">
                <History className="w-4 h-4 text-[var(--color-accent)]" /> Approval Audit History
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              {approvals.length === 0 ? (
                <div className="text-center py-6 text-sm text-[var(--color-text-tertiary)]">
                  No approval records have been logged for this draft.
                </div>
              ) : (
                <div className="space-y-4">
                  {approvals.map(app => (
                    <div
                      key={app.id}
                      className="p-4 rounded-xl border border-[var(--color-border-primary)] bg-[var(--color-bg-subtle)] space-y-2"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-sm text-[var(--color-text-primary)]">
                            Status:
                          </span>
                          {getDraftStatusBadge(app.status)}
                        </div>
                        <span className="text-xs text-[var(--color-text-muted)]">
                          {new Date(app.created_at).toLocaleString()}
                        </span>
                      </div>
                      {app.review_comment && (
                        <p className="text-xs text-[var(--color-text-secondary)] bg-[var(--color-bg-surface)] p-2.5 rounded border border-[var(--color-border-primary)]">
                          <span className="font-semibold">Comment:</span> {app.review_comment}
                        </p>
                      )}
                      <div className="flex items-center gap-4 text-xs text-[var(--color-text-muted)]">
                        <span>Requested By: <code className="font-mono">{app.requested_by.slice(0, 8)}</code></span>
                        {app.reviewed_by && (
                          <span>Reviewed By: <code className="font-mono">{app.reviewed_by.slice(0, 8)}</code></span>
                        )}
                        {app.reviewed_at && (
                          <span>At: {new Date(app.reviewed_at).toLocaleString()}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Publication Pipeline & Controls */}
        <div className="space-y-6">
          {/* Publication Status Card */}
          <Card className="border-[var(--color-border-primary)] bg-[var(--color-bg-surface)] overflow-hidden">
            <CardHeader className="border-b border-[var(--color-border-primary)] py-4 px-6 bg-[var(--color-bg-subtle)]">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base font-semibold flex items-center gap-2">
                  <Share2 className="w-4 h-4 text-[var(--color-accent)]" /> Publication Status
                </CardTitle>
                {publication ? (
                  getPubStatusBadge(publication.status)
                ) : (
                  <Badge variant="outline" className="text-xs">NOT DISPATCHED</Badge>
                )}
              </div>
            </CardHeader>

            <CardContent className="p-6 space-y-5">
              {/* Publication Status Banner */}
              {publication ? (
                <div className="space-y-4">
                  {/* Status specific notices */}
                  {publication.status === 'PUBLISHED' && (
                    <div className="p-4 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 space-y-2">
                      <div className="flex items-center gap-2 text-emerald-800 dark:text-emerald-300 font-semibold text-sm">
                        <Check className="w-4 h-4" /> Published Confirmed
                      </div>
                      <p className="text-xs text-emerald-700 dark:text-emerald-400">
                        Platform: <span className="font-semibold uppercase">{publication.platform}</span>
                      </p>
                      {publication.external_post_id && (
                        <p className="text-xs text-emerald-700 dark:text-emerald-400 font-mono break-all">
                          ID: {publication.external_post_id}
                        </p>
                      )}
                      {publication.published_at && (
                        <p className="text-xs text-emerald-600 dark:text-emerald-500">
                          {new Date(publication.published_at).toLocaleString()}
                        </p>
                      )}
                    </div>
                  )}

                  {publication.status === 'PUBLISHING' && (
                    <div className="p-4 rounded-xl bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800 space-y-1">
                      <div className="flex items-center gap-2 text-blue-800 dark:text-blue-300 font-semibold text-sm">
                        <RefreshCw className="w-4 h-4 animate-spin" /> In Flight
                      </div>
                      <p className="text-xs text-blue-700 dark:text-blue-400">
                        Publishing worker is currently executing dispatch to {publication.platform}.
                      </p>
                    </div>
                  )}

                  {publication.status === 'QUEUED' && (
                    <div className="p-4 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 space-y-1">
                      <div className="flex items-center gap-2 text-amber-800 dark:text-amber-300 font-semibold text-sm">
                        <Clock className="w-4 h-4" /> Queued for Worker
                      </div>
                      <p className="text-xs text-amber-700 dark:text-amber-400">
                        Waiting in queue for Celery publishing worker pick-up.
                      </p>
                    </div>
                  )}

                  {(publication.status === 'FAILED' || publication.status === 'BLOCKED') && (
                    <div className="p-4 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 space-y-2">
                      <div className="flex items-center gap-2 text-red-800 dark:text-red-300 font-semibold text-sm">
                        <XCircle className="w-4 h-4" /> {publication.status === 'BLOCKED' ? 'Publishing Blocked' : 'Publication Failed'}
                      </div>
                      {publication.error_code && (
                        <p className="text-xs font-mono font-semibold text-red-700 dark:text-red-400">
                          Error Code: {publication.error_code}
                        </p>
                      )}
                      {publication.error_message && (
                        <p className="text-xs text-red-600 dark:text-red-400">
                          {publication.error_message}
                        </p>
                      )}
                      <Button
                        size="sm"
                        disabled={actionLoading || !isApproved}
                        onClick={handlePublish}
                        className="w-full mt-2 bg-red-600 hover:bg-red-700 text-white flex items-center justify-center gap-1.5"
                      >
                        <RotateCcw className="w-3.5 h-3.5" /> Retry Dispatch
                      </Button>
                    </div>
                  )}

                  {/* RECONCILIATION_REQUIRED Safety State */}
                  {publication.status === 'RECONCILIATION_REQUIRED' && (
                    <div className="p-5 rounded-xl bg-amber-500/10 border-2 border-amber-500/40 space-y-3">
                      <div className="flex items-center gap-2 text-amber-700 dark:text-amber-400 font-semibold text-sm">
                        <ShieldAlert className="w-5 h-5" /> Uncertain Outcome
                      </div>
                      <p className="text-xs text-amber-800 dark:text-amber-300 leading-relaxed">
                        The publication timed out or encountered an unconfirmed state. Automatic retries are locked to avoid accidental double-posting. Manual reconciliation is required.
                      </p>
                      <Button
                        size="sm"
                        onClick={() => setReconciling(true)}
                        className="w-full bg-amber-600 hover:bg-amber-700 text-white font-medium"
                      >
                        Reconcile Publication
                      </Button>
                    </div>
                  )}
                </div>
              ) : (
                /* No publication record yet */
                <div className="space-y-4">
                  {isApproved ? (
                    <div className="space-y-4">
                      <div className="p-3 bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800 rounded-lg text-xs text-emerald-800 dark:text-emerald-300 flex items-center gap-2">
                        <CheckCircle2 className="w-4 h-4 shrink-0" />
                        <span>Approval verified. Draft is ready for publication.</span>
                      </div>

                      {/* Platform selector */}
                      <div className="space-y-2">
                        <label className="block text-xs font-medium text-[var(--color-text-secondary)]">
                          Select Destination Platform:
                        </label>
                        {connectedPlatforms.length === 0 ? (
                          <div className="p-4 border border-dashed border-[var(--color-border-primary)] rounded-lg text-center space-y-2">
                            <p className="text-xs text-[var(--color-text-tertiary)]">
                              No publishing accounts currently connected.
                            </p>
                            <Link href="/app/integrations">
                              <Button variant="outline" size="sm" className="text-xs">
                                Connect Integrations
                              </Button>
                            </Link>
                          </div>
                        ) : (
                          <div className="grid grid-cols-2 gap-2">
                            {connectedPlatforms.map(p => (
                              <button
                                key={p.platform}
                                type="button"
                                onClick={() => setSelectedPlatform(p.platform)}
                                className={`p-3 rounded-lg border text-left text-xs transition-all ${
                                  selectedPlatform === p.platform
                                    ? 'border-[var(--color-accent)] bg-[var(--color-accent)]/10 font-semibold text-[var(--color-text-primary)]'
                                    : 'border-[var(--color-border-primary)] bg-[var(--color-bg-base)] text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-subtle)]'
                                }`}
                              >
                                <div className="capitalize font-medium">{p.platform}</div>
                                {p.external_account_name && (
                                  <div className="text-[10px] text-[var(--color-text-muted)] truncate">
                                    {p.external_account_name}
                                  </div>
                                )}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>

                      <Button
                        disabled={actionLoading || connectedPlatforms.length === 0}
                        onClick={handlePublish}
                        className="w-full bg-[var(--color-accent)] hover:opacity-90 text-white flex items-center justify-center gap-2"
                      >
                        <Share2 className="w-4 h-4" />
                        {actionLoading ? 'Dispatching...' : `Publish to ${selectedPlatform}`}
                      </Button>
                    </div>
                  ) : (
                    <div className="p-4 rounded-xl border border-[var(--color-border-primary)] bg-[var(--color-bg-subtle)] text-center space-y-2">
                      <Clock className="w-6 h-6 text-[var(--color-text-muted)] mx-auto" />
                      <p className="text-xs font-semibold text-[var(--color-text-primary)]">
                        Approval Required Prior to Publishing
                      </p>
                      <p className="text-xs text-[var(--color-text-tertiary)]">
                        Under tenant governance rules, content must hold an active APPROVED record before dispatch.
                      </p>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Publication Attempts Log */}
          {publication && publication.attempts && publication.attempts.length > 0 && (
            <Card className="border-[var(--color-border-primary)] bg-[var(--color-bg-surface)]">
              <CardHeader className="py-3 px-6 border-b border-[var(--color-border-primary)]">
                <CardTitle className="text-xs uppercase tracking-wider font-semibold text-[var(--color-text-muted)] flex items-center justify-between">
                  <span>Dispatch Attempts</span>
                  <Badge variant="outline" className="font-mono text-[10px]">
                    {publication.attempts.length} attempts
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4 space-y-3">
                {publication.attempts.map((att, idx) => (
                  <div
                    key={att.id}
                    className="p-3 rounded-lg border border-[var(--color-border-primary)] bg-[var(--color-bg-base)] text-xs space-y-1.5"
                  >
                    <div className="flex items-center justify-between font-mono">
                      <span className="font-semibold text-[var(--color-text-primary)]">
                        Attempt #{att.attempt_number || idx + 1}
                      </span>
                      <Badge
                        variant={att.status === 'SUCCESS' ? 'success' : att.status === 'FAILED' ? 'danger' : 'warning'}
                        className="text-[10px]"
                      >
                        {att.status}
                      </Badge>
                    </div>
                    <div className="text-[10px] text-[var(--color-text-muted)]">
                      Started: {new Date(att.started_at).toLocaleString()}
                    </div>
                    {att.error_code && (
                      <div className="text-red-500 font-mono text-[10px]">
                        [{att.error_code}] {att.error_message}
                      </div>
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Reconciliation Modal */}
      {reconciling && publication && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <Card className="w-full max-w-lg border-[var(--color-border-primary)] bg-[var(--color-bg-surface)] shadow-2xl">
            <CardHeader className="border-b border-[var(--color-border-primary)] py-4 px-6">
              <CardTitle className="text-lg font-semibold flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-amber-500" />
                Reconcile Publication
              </CardTitle>
              <p className="text-xs text-[var(--color-text-tertiary)] mt-1">
                Resolve uncertain state for draft publication on {publication.platform}.
              </p>
            </CardHeader>

            <CardContent className="p-6 space-y-4">
              <div className="space-y-2">
                <label className="block text-xs font-semibold text-[var(--color-text-secondary)]">
                  Resolution Action:
                </label>
                <div className="grid grid-cols-3 gap-2">
                  <button
                    type="button"
                    onClick={() => setReconcileResolution('PUBLISHED')}
                    className={`p-2.5 rounded-lg border text-xs font-medium text-center ${
                      reconcileResolution === 'PUBLISHED'
                        ? 'border-emerald-500 bg-emerald-50 text-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300'
                        : 'border-[var(--color-border-primary)] text-[var(--color-text-secondary)]'
                    }`}
                  >
                    Confirm Published
                  </button>
                  <button
                    type="button"
                    onClick={() => setReconcileResolution('FAILED')}
                    className={`p-2.5 rounded-lg border text-xs font-medium text-center ${
                      reconcileResolution === 'FAILED'
                        ? 'border-red-500 bg-red-50 text-red-800 dark:bg-red-950/40 dark:text-red-300'
                        : 'border-[var(--color-border-primary)] text-[var(--color-text-secondary)]'
                    }`}
                  >
                    Mark Failed
                  </button>
                  <button
                    type="button"
                    onClick={() => setReconcileResolution('RETRY')}
                    className={`p-2.5 rounded-lg border text-xs font-medium text-center ${
                      reconcileResolution === 'RETRY'
                        ? 'border-blue-500 bg-blue-50 text-blue-800 dark:bg-blue-950/40 dark:text-blue-300'
                        : 'border-[var(--color-border-primary)] text-[var(--color-text-secondary)]'
                    }`}
                  >
                    Safe Retry
                  </button>
                </div>
              </div>

              {reconcileResolution === 'PUBLISHED' && (
                <div className="space-y-1.5">
                  <label className="block text-xs font-semibold text-[var(--color-text-secondary)]">
                    External Post ID (Required):
                  </label>
                  <input
                    type="text"
                    value={reconcileExternalId}
                    onChange={e => setReconcileExternalId(e.target.value)}
                    placeholder="e.g. urn:li:share:7182910291 or 12345"
                    className="w-full text-xs p-2.5 rounded-lg border border-[var(--color-border-primary)] bg-[var(--color-bg-base)] text-[var(--color-text-primary)] font-mono focus:outline-none"
                  />
                  <p className="text-[10px] text-[var(--color-text-muted)]">
                    Never mark a post as published unless confirmed on the external platform.
                  </p>
                </div>
              )}

              <div className="space-y-1.5">
                <label className="block text-xs font-semibold text-[var(--color-text-secondary)]">
                  Notes / Audit Justification:
                </label>
                <textarea
                  rows={2}
                  value={reconcileNotes}
                  onChange={e => setReconcileNotes(e.target.value)}
                  placeholder="Explain why this reconciliation action was chosen..."
                  className="w-full text-xs p-2.5 rounded-lg border border-[var(--color-border-primary)] bg-[var(--color-bg-base)] text-[var(--color-text-primary)] focus:outline-none"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-[var(--color-border-primary)]">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setReconciling(false)
                    setReconcileExternalId('')
                    setReconcileNotes('')
                  }}
                >
                  Cancel
                </Button>
                <Button
                  size="sm"
                  disabled={actionLoading || (reconcileResolution === 'PUBLISHED' && !reconcileExternalId.trim())}
                  onClick={handleReconcile}
                  className="bg-[var(--color-accent)] text-white"
                >
                  {actionLoading ? 'Applying...' : 'Apply Resolution'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
