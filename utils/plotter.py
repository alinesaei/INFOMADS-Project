import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict, Optional
from core.data_models import Job, ScheduleResult
import plotly.express as px


def create_gantt_chart(
        jobs: List[Job],
        result: Optional[ScheduleResult],
        T_max: int,
        visible_jobs: Optional[List[int]] = None
):

    if not jobs:
        return go.Figure()

    if visible_jobs is None:
        visible_jobs = [job.id for job in jobs]

    jobs_to_display = [job for job in jobs if job.id in visible_jobs]
    if not jobs_to_display:
        return go.Figure(layout_title_text="No jobs selected to display.")

    color_palette = px.colors.qualitative.Plotly
    job_colors = {job.id: color_palette[i % len(color_palette)] for i, job in enumerate(jobs)}

    df_list = []
    # Windows
    for job in jobs_to_display:
        df_list.append(dict(
            Task=f"Job {job.id}", Type='Window', Start=job.r_j, Finish=job.d_j, JobId=job.id,
            Details=f"p={job.p_j}, r={job.r_j}, d={job.d_j}, w={job.w_j}, l={job.l_j}"
        ))
    # Scheduled Blocks
    if result and result.schedule:
        schedule = {t: jid for t, jid in result.schedule.items() if jid in visible_jobs}
        slots_by_job = {}
        for time, job_id in schedule.items():
            slots_by_job.setdefault(job_id, []).append(time)

        for job_id, slots in slots_by_job.items():
            job = next((j for j in jobs if j.id == job_id), None)
            if not job: continue

            slots.sort()
            start_slot = slots[0]
            for i in range(1, len(slots)):
                if slots[i] != slots[i - 1] + 1:
                    df_list.append(dict(
                        Task=f"Job {job_id}", Type='Scheduled', Start=start_slot, Finish=slots[i - 1] + 1, JobId=job_id,
                        Details=f"p={job.p_j}, r={job.r_j}, d={job.d_j}, w={job.w_j}, l={job.l_j}"
                    ))
                    start_slot = slots[i]
            df_list.append(dict(
                Task=f"Job {job_id}", Type='Scheduled', Start=start_slot, Finish=slots[-1] + 1, JobId=job_id,
                Details=f"p={job.p_j}, r={job.r_j}, d={job.d_j}, w={job.w_j}, l={job.l_j}"
            ))

    if not df_list:
        return go.Figure(layout_title_text="No data to display for selected jobs.")

    df = pd.DataFrame(df_list)
    fig = go.Figure()

    # --- Add traces layer by layer ---
    for job_id in df['JobId'].unique():
        job_df = df[df['JobId'] == job_id]
        job_color = job_colors[job_id]

        # Add faint window bars
        window_df = job_df[job_df['Type'] == 'Window']
        fig.add_trace(go.Bar(
            y=window_df['Task'],
            x=window_df['Finish'] - window_df['Start'],
            base=window_df['Start'],
            orientation='h',
            marker_color=job_color,
            opacity=0.3,
            name=f"Job {job_id} Window",
            customdata=window_df['Details'],
            hovertemplate='<b>%{y}</b> (Window)<br>Available: %{base}-%{base|add:%{x}}<br><b>Details:</b> %{customdata}<extra></extra>'
        ))

        # Add solid scheduled bars
        scheduled_df = job_df[job_df['Type'] == 'Scheduled']
        fig.add_trace(go.Bar(
            y=scheduled_df['Task'],
            x=scheduled_df['Finish'] - scheduled_df['Start'],
            base=scheduled_df['Start'],
            orientation='h',
            marker_color=job_color,
            opacity=1.0,
            name=f"Job {job_id} Scheduled",
            customdata=scheduled_df['Details'],
            hovertemplate='<b>%{y}</b> (Scheduled)<br>Timeslots: %{base}-%{base|add:%{x}}<br><b>Details:</b> %{customdata}<extra></extra>'
        ))

    fig.update_layout(
        title_text='Job Schedule Visualization',
        xaxis_title='Time Slot',
        yaxis_title='Jobs',
        xaxis=dict(tickmode='linear', tick0=1, dtick=1, range=[0, T_max + 1]),
        plot_bgcolor='white',
        barmode='stack',
        legend_title_text='Trace Type',
        font=dict(family="Arial, sans-serif", size=12, color="black"),
    )
    # Sort Y-axis to have Job 1 at the top
    fig.update_yaxes(categoryorder='array', categoryarray=sorted(df['Task'].unique(), reverse=True))

    return fig