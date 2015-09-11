package uk.ac.diamond.optid.properties;

import org.eclipse.core.runtime.preferences.AbstractPreferenceInitializer;
import org.eclipse.jface.preference.IPreferenceStore;

import uk.ac.diamond.optid.Activator;

public class PropertyInitializer extends AbstractPreferenceInitializer {

	@Override
	public void initializeDefaultPreferences() {
		IPreferenceStore store = Activator.getDefault().getPreferenceStore();
		
		store.setDefault(PropertyConstants.P_WORK_DIR, System.getProperty("user.home"));
		
		// Add ID Description constants
		store.setDefault(IdDescPropertyConstants.P_ID_DESC_NAME, IdDescPropertyConstants.DEF_ID_DESC_NAME);
		store.setDefault(IdDescPropertyConstants.P_ID_DESC_TYPE, IdDescPropertyConstants.DEF_ID_DESC_TYPE);
		store.setDefault(IdDescPropertyConstants.P_ID_DESC_PERIODS, IdDescPropertyConstants.DEF_ID_DESC_PERIODS);
		store.setDefault(IdDescPropertyConstants.P_ID_DESC_GAP, IdDescPropertyConstants.DEF_ID_DESC_GAP);
		store.setDefault(IdDescPropertyConstants.P_ID_DESC_INTERSTICE, IdDescPropertyConstants.DEF_ID_DESC_INTERSTICE);
		store.setDefault(IdDescPropertyConstants.P_ID_DESC_FULL_X, IdDescPropertyConstants.DEF_ID_DESC_FULL_X);
		store.setDefault(IdDescPropertyConstants.P_ID_DESC_FULL_Z, IdDescPropertyConstants.DEF_ID_DESC_FULL_Z);
		store.setDefault(IdDescPropertyConstants.P_ID_DESC_FULL_S, IdDescPropertyConstants.DEF_ID_DESC_FULL_S);
		store.setDefault(IdDescPropertyConstants.P_ID_DESC_VE_X, IdDescPropertyConstants.DEF_ID_DESC_VE_X);
		store.setDefault(IdDescPropertyConstants.P_ID_DESC_VE_Z, IdDescPropertyConstants.DEF_ID_DESC_VE_Z);
		store.setDefault(IdDescPropertyConstants.P_ID_DESC_VE_S, IdDescPropertyConstants.DEF_ID_DESC_VE_S);
		store.setDefault(IdDescPropertyConstants.P_ID_DESC_HE_X, IdDescPropertyConstants.DEF_ID_DESC_HE_X);
		store.setDefault(IdDescPropertyConstants.P_ID_DESC_HE_Z, IdDescPropertyConstants.DEF_ID_DESC_HE_Z);
		store.setDefault(IdDescPropertyConstants.P_ID_DESC_HE_S, IdDescPropertyConstants.DEF_ID_DESC_HE_S);
		store.setDefault(IdDescPropertyConstants.P_ID_DESC_X_START, IdDescPropertyConstants.DEF_ID_DESC_X_START);
		store.setDefault(IdDescPropertyConstants.P_ID_DESC_X_STOP, IdDescPropertyConstants.DEF_ID_DESC_X_STOP);
		store.setDefault(IdDescPropertyConstants.P_ID_DESC_X_STEP, IdDescPropertyConstants.DEF_ID_DESC_X_STEP);
		store.setDefault(IdDescPropertyConstants.P_ID_DESC_Z_START, IdDescPropertyConstants.DEF_ID_DESC_Z_START);
		store.setDefault(IdDescPropertyConstants.P_ID_DESC_Z_STOP, IdDescPropertyConstants.DEF_ID_DESC_Z_STOP);
		store.setDefault(IdDescPropertyConstants.P_ID_DESC_Z_STEP, IdDescPropertyConstants.DEF_ID_DESC_Z_STEP);
		store.setDefault(IdDescPropertyConstants.P_ID_DESC_STEPS_S, IdDescPropertyConstants.DEF_ID_DESC_STEPS_S);
		store.setDefault(IdDescPropertyConstants.P_ID_DESC_END_GAP, IdDescPropertyConstants.DEF_ID_DESC_END_GAP);
		store.setDefault(IdDescPropertyConstants.P_ID_DESC_PHASING_GAP, IdDescPropertyConstants.DEF_ID_DESC_PHASING_GAP);
		store.setDefault(IdDescPropertyConstants.P_ID_DESC_CLAMP_CUT, IdDescPropertyConstants.DEF_ID_DESC_CLAMP_CUT);
	}

}
