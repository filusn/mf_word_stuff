import MenuIcon from '@mui/icons-material/Menu';
import ShieldIcon from '@mui/icons-material/Shield';
import { IconButton, Tooltip, Typography } from '@mui/material';

export default function Navbar(): JSX.Element {
    return <div style={{display: 'flex', justifyContent: 'space-between', paddingTop: '1em', paddingRight: '1em'}}>
        

        <Tooltip title='Menu'>
        <IconButton ><MenuIcon/></IconButton>
        </Tooltip>
    </div>
}