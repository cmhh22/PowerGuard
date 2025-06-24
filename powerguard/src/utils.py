def filter_pending(outages):
    """Devuelve una lista de outages pendientes (no resueltos)."""
    return [o for o in outages if not o.resolved]

def format_outages(outages):
    """Devuelve un string legible con la información de los outages."""
    lines = []
    for o in outages:
        status = 'Resolved' if o.resolved else 'Pending'
        duration = f"{o.duration_estimated} min" if o.duration_estimated is not None else "N/A"
        lines.append(
            f"ID: {o.id} | Zone: {o.zone} | Start: {o.start_time.strftime('%Y-%m-%d %H:%M')} | "
            f"Estimated Duration: {duration} | Status: {status}"
        )
    return '\n'.join(lines)

def format_csv(outages):
    """Devuelve un string CSV con los outages."""
    header = 'id,zone,start_time,duration_estimated,resolved,resolved_time'
    rows = [header]
    for o in outages:
        rows.append(','.join([
            str(o.id),
            o.zone,
            o.start_time.isoformat(),
            str(o.duration_estimated) if o.duration_estimated is not None else '',
            str(o.resolved),
            o.resolved_time.isoformat() if o.resolved_time else ''
        ]))
    return '\n'.join(rows)